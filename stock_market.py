import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

# Streamlit UI setup
st.set_page_config(page_title="Real-Time Stock Dashboard", layout="wide")
st.sidebar.title("Stock Market Dashboard")

# Sidebar inputs
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL, TSLA):", value="AAPL").upper()
interval = st.sidebar.selectbox("Interval", ['1m', '5m', '15m', '1h', '1d'])
days = st.sidebar.slider("Past Days to Load:", 1, 30, 5)

# Main Title
st.title(f"📈 Real-Time Dashboard: {ticker}")

# Safe data fetch function
@st.cache_data(ttl=300)
def load_data(ticker, interval, days):
    try:
        # Mapping days to period supported by yfinance for each interval
        period_map = {
            "1m": f"{min(days, 5)}d",     # yfinance allows max ~7 days for 1m
            "5m": f"{min(days, 30)}d",
            "15m": f"{min(days, 30)}d",
            "1h": f"{min(days, 60)}d",
            "1d": f"{days}d"
        }
        period = period_map.get(interval, f"{days}d")

        # Download data
        data = yf.download(ticker, period=period, interval=interval)
        if data.empty:
            raise ValueError("No data returned. Try different interval or fewer days.")
        data.dropna(inplace=True)
        return data
    except Exception as e:
        raise e

# Try to load and visualize data
try:
    data = load_data(ticker, interval, days)

    # Show the latest price with delta
    latest_price = float(data['Close'].iloc[-1])
    open_price = float(data['Open'].iloc[-1])
    delta = latest_price - open_price
    st.metric(label="Last Price", value=f"${latest_price:.2f}", delta=f"{delta:.2f}")

    # Line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close Price', line=dict(color='cyan')))
    fig.update_layout(title="Stock Price Over Time", xaxis_title="Time", yaxis_title="Price (USD)", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # Volume bar chart
    st.subheader("Volume Chart")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volume', marker_color='orange'))
    fig2.update_layout(template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

    # Optional raw data
    if st.checkbox("Show Raw Data"):
        st.dataframe(data.tail(20))

except Exception as e:
    st.error("⚠️ Could not load stock data. Please adjust the interval or number of days.")
    st.exception(e)
