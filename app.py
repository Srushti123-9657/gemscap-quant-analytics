print(">>> app.py started")

import json
import threading
import sqlite3
from flask import Flask, render_template, jsonify
from websocket import WebSocketApp

import pandas as pd
import statsmodels.api as sm

# ---------------- FLASK APP ----------------
app = Flask(__name__)

DB = "ticks.db"
SYMBOLS = ["btcusdt", "ethusdt"]
ws_started = False   # start WS only once


# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS ticks (
            ts INTEGER,
            symbol TEXT,
            price REAL,
            qty REAL
        )
    """)
    conn.commit()
    conn.close()


# ---------------- WEBSOCKET ----------------
def on_message(ws, message):
    data = json.loads(message)
    if "p" in data:
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute(
            "INSERT INTO ticks VALUES (?, ?, ?, ?)",
            (data["T"], data["s"].lower(), float(data["p"]), float(data["q"]))
        )
        conn.commit()
        conn.close()


def start_ws(symbol):
    url = f"wss://fstream.binance.com/ws/{symbol}@trade"
    ws = WebSocketApp(url, on_message=on_message)
    ws.run_forever()


def start_streams_once():
    global ws_started
    if ws_started:
        return
    ws_started = True
    print(">>> Starting WebSocket streams")
    for s in SYMBOLS:
        t = threading.Thread(target=start_ws, args=(s,), daemon=True)
        t.start()


# ---------------- ANALYTICS ----------------
def compute_analytics():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM ticks", conn)
    conn.close()

    if df.empty:
        return {}

    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    df = df.set_index("ts")

    btc = df[df["symbol"] == "btcusdt"]["price"].resample("1min").last()
    eth = df[df["symbol"] == "ethusdt"]["price"].resample("1min").last()

    data = pd.concat([btc, eth], axis=1)
    data.columns = ["btc", "eth"]
    data.dropna(inplace=True)

    if len(data) < 5:
        return {}

    # Hedge ratio using OLS
    X = sm.add_constant(data["eth"])
    model = sm.OLS(data["btc"], X).fit()
    hedge_ratio = model.params[1]

    spread = data["btc"] - hedge_ratio * data["eth"]
    zscore = (spread - spread.mean()) / spread.std()

    # -------- ALERT LOGIC --------
    alert = None
    latest_z = zscore.iloc[-1]
    if abs(latest_z) > 2:
        alert = f"ALERT: Z-score crossed ±2 (Current: {round(latest_z, 2)})"

    return {
        "spread": spread.tolist(),
        "zscore": zscore.tolist(),
        "hedge_ratio": round(float(hedge_ratio), 4),
        "alert": alert
    }


# ---------------- ROUTES ----------------
@app.route("/")
def index():
    start_streams_once()   # start WS AFTER Flask is live
    return render_template("index.html")


@app.route("/data")
def data():
    return jsonify(compute_analytics())


# ---------------- MAIN ----------------
if __name__ == "__main__":
    print(">>> ENTERED MAIN BLOCK")
    print(">>> Initializing database")
    init_db()

    print(">>> Starting Flask server")
    app.run(host="127.0.0.1", port=5000, debug=False)