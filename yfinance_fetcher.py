import yfinance as yf
import pandas as pd
import json
from ta.momentum import RSIIndicator
from ta.trend import MACD

# Function to calculate VWAP manually
def calculate_vwap(data):
    typical_price = (data['High'] + data['Low'] + data['Close']) / 3
    vwap = (typical_price * data['Volume']).cumsum() / data['Volume'].cumsum()
    return vwap

def get_stock_data(ticker):
    try:
        # Download data for the ticker (5 columns: Open, High, Low, Close, Volume)
        data = yf.download(ticker, period='6mo', interval='1d', progress=False, auto_adjust=True)
        if data.empty:
            return None
        
        # Flatten the MultiIndex columns
        data.columns = data.columns.get_level_values(0)  # Drop the second level from the MultiIndex

        # Print to debug data shape and columns after flattening
        print(f"Downloaded data for {ticker}: {data.shape}")
        print(f"Columns after flattening: {data.columns}")

        # Ensure we're working with Series for indicators (1D array)
        close_prices = data['Close']
        high_prices = data['High']
        low_prices = data['Low']
        volume = data['Volume']

        # Compute technical indicators
        rsi_indicator = RSIIndicator(close=close_prices)
        data['RSI'] = rsi_indicator.rsi()

        # Moving Averages (20, 50, 200)
        data['MA_20'] = close_prices.rolling(window=20).mean()
        data['MA_50'] = close_prices.rolling(window=50).mean()
        data['MA_200'] = close_prices.rolling(window=200).mean()

        # MACD
        macd_indicator = MACD(close=close_prices)
        data['MACD'] = macd_indicator.macd()
        data['MACD_Signal'] = macd_indicator.macd_signal()

        # VWAP calculation
        data['VWAP'] = calculate_vwap(data)

        # Return data in structured format
        return {
            "price_movement": data['Close'].dropna().tolist(),
            "rsi": data['RSI'].dropna().tolist(),
            "moving_averages": {
                "ma_20": data['MA_20'].dropna().tolist(),
                "ma_50": data['MA_50'].dropna().tolist(),
                "ma_200": data['MA_200'].dropna().tolist(),
            },
            "macd": {
                "macd": data['MACD'].dropna().tolist(),
                "macd_signal": data['MACD_Signal'].dropna().tolist()
            },
            "vwap": data['VWAP'].dropna().tolist()
        }

    except Exception as e:
        print(f"Error for {ticker}: {e}")
        return None

def build_perception_json(nse_ticker=None, bse_ticker=None, output_json_path="yf_stats.json"):
    result = {}

    if nse_ticker:
        nse_full_ticker = f"{nse_ticker}.NS"
        nse_data = get_stock_data(nse_full_ticker)
        if nse_data:
            result["NSE"] = nse_data

    if bse_ticker:
        bse_full_ticker = f"{bse_ticker}.BO"
        bse_data = get_stock_data(bse_full_ticker)
        if bse_data:
            result["BSE"] = bse_data

    with open(output_json_path, "w") as f:
        json.dump(result, f, indent=2)