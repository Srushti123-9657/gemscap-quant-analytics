\# Gemscap Quant Analytics Assignment



\## Overview

This project is a real-time quantitative analytics dashboard developed as part of the Gemscap Quant Developer evaluation assignment.



The system ingests live cryptocurrency trade data from Binance Futures using WebSocket streams, stores and processes the data, computes key pair-trading analytics, and visualizes the results through an interactive web dashboard.



---



\## Features

\- Live data ingestion from Binance Futures (BTCUSDT \& ETHUSDT)

\- SQLite database for storing tick-level data

\- 1-minute resampling of price data

\- Hedge ratio estimation using OLS regression

\- Spread and Z-score computation for pair trading

\- Real-time interactive dashboard using Flask and Plotly

\- Alert displayed when Z-score crosses ±2



---



\## Tech Stack

\- Python 3.11

\- Flask

\- SQLite

\- Pandas

\- Statsmodels

\- Plotly

\- Binance WebSocket API



---



\## How to Run the Project



\### Step 1: Install dependencies

```bash pip install -r requirements.txt

\### Step 2:Run the application

&nbsp;	Python app.py

\### Step 3: Open the Dashboard

&nbsp;	http://127.0.0.1:5000

&nbsp;



\## System Architecture



!\[System Architecture](system\_architecture.jpg)



Binance WebSocket  

→ Flask Backend (Data Ingestion \& APIs)  

→ SQLite Database  

→ Analytics Engine (OLS, Spread, Z-score)  

→ Plotly Dashboard

