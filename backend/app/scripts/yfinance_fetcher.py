# import yfinance as yf
# import pandas as pd
# import json
# from ta.momentum import RSIIndicator
# from ta.trend import MACD
# from bs4 import BeautifulSoup
# import requests
# from duckduckgo_search import DDGS

# # Function to calculate VWAP manually
# def calculate_vwap(data):
#     typical_price = (data['High'] + data['Low'] + data['Close']) / 3
#     vwap = (typical_price * data['Volume']).cumsum() / data['Volume'].cumsum()
#     return vwap

# def get_stock_data(ticker):
#     try:
#         # Download data for the ticker (5 columns: Open, High, Low, Close, Volume)
#         data = yf.download(ticker, period='6mo', interval='1d', progress=False, auto_adjust=True)
#         if data.empty:
#             return None
        
#         # Flatten the MultiIndex columns
#         data.columns = data.columns.get_level_values(0)  # Drop the second level from the MultiIndex

#         # Print to debug data shape and columns after flattening
#         print(f"Downloaded data for {ticker}: {data.shape}")
#         print(f"Columns after flattening: {data.columns}")

#         # Ensure i'm working with Series for indicators (1D array)
#         close_prices = data['Close']
#         high_prices = data['High']
#         low_prices = data['Low']
#         volume = data['Volume']

#         # Compute technical indicators
#         rsi_indicator = RSIIndicator(close=close_prices)
#         data['RSI'] = rsi_indicator.rsi()

#         # Moving Averages (20, 50, 200)
#         data['MA_20'] = close_prices.rolling(window=20).mean()
#         data['MA_50'] = close_prices.rolling(window=50).mean()
#         data['MA_200'] = close_prices.rolling(window=200).mean()

#         # MACD
#         macd_indicator = MACD(close=close_prices)
#         data['MACD'] = macd_indicator.macd()
#         data['MACD_Signal'] = macd_indicator.macd_signal()

#         # VWAP calculation
#         data['VWAP'] = calculate_vwap(data)

#         # Return data in structured format
#         return {
#             "price_movement": data['Close'].dropna().tolist(),
#             "rsi": data['RSI'].dropna().tolist(),
#             "moving_averages": {
#                 "ma_20": data['MA_20'].dropna().tolist(),
#                 "ma_50": data['MA_50'].dropna().tolist(),
#                 "ma_200": data['MA_200'].dropna().tolist(),
#             },
#             "macd": {
#                 "macd": data['MACD'].dropna().tolist(),
#                 "macd_signal": data['MACD_Signal'].dropna().tolist()
#             },
#             "vwap": data['VWAP'].dropna().tolist()
#         }

#     except Exception as e:
#         print(f"Error for {ticker}: {e}")
#         return None

# def build_perception_json(nse_ticker=None, bse_ticker=None, output_json_path="yf_stats.json"):
#     result = {}

#     if nse_ticker:
#         nse_full_ticker = f"{nse_ticker}.NS"
#         nse_data = get_stock_data(nse_full_ticker)
#         if nse_data:
#             result["NSE"] = nse_data

#     if bse_ticker:
#         bse_full_ticker = f"{bse_ticker}.BO"
#         bse_data = get_stock_data(bse_full_ticker)
#         if bse_data:
#             result["BSE"] = bse_data

#     with open(output_json_path, "w") as f:
#         json.dump(result, f, indent=2)

# def yfinance_full(company_name, output_path="yf_stats.json"):
#     nse_ticker=get_nse_ticker(company_name)
#     bse_ticker=get_bse_ticker(company_name)
#     build_perception_json(nse_ticker=nse_ticker, bse_ticker=bse_ticker, output_json_path=output_path)

# # def get_nse_ticker(company_name):
# #     query=f'site:screener.in "{company_name}"'
# #     target_url=None
# #     for result in search(query, num_results=1):
# #         if "screener.in" in result:
# #             target_url = result
# #     if not target_url:
# #         return None
# #     headers = {
# #         "User-Agent": "Mozilla/5.0"
# #     }
# #     response = requests.get(target_url, headers=headers)
# #     if response.status_code != 200:
# #         return None
# #     soup = BeautifulSoup(response.text, 'html.parser')
# #     element = soup.select_one("a~ a+ a .upper")
# #     if element:
# #         tmp_text=element.get_text(strip=True)
# #         return tmp_text[4:].strip()
# #     else:
# #         return None
# def get_nse_ticker(company_name):
#     query = f'site:screener.in "{company_name}"'
#     target_url = None

#     # Use DuckDuckGo search to get the first result
#     ddgs=DDGS(timeout=30)
#     results = ddgs.text(query, max_results=1)
#     if results:
#         # DuckDuckGo returns a list of dicts with 'href' as the URL
#         first_result = results[0]
#         if "screener.in" in first_result.get("href", ""):
#             target_url = first_result["href"]

#     if not target_url:
#         return None

#     headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
#     }
#     response = requests.get(target_url, headers=headers)
#     if response.status_code != 200:
#         return None
#     soup = BeautifulSoup(response.text, 'html.parser')
#     element = soup.select_one("a~ a+ a .upper")
#     if element:
#         tmp_text = element.get_text(strip=True)
#         return tmp_text[4:].strip()
#     else:
#         return None

# def get_bse_ticker(company_name):
#     query = f'site:screener.in "{company_name}"'
#     target_url = None

#     # Use DuckDuckGo search to get the first result
#     ddgs=DDGS(timeout=30)
#     results = ddgs.text(query, max_results=1)
#     if results:
#         # DuckDuckGo returns a list of dicts with 'href' as the URL
#         first_result = results[0]
#         if "screener.in" in first_result.get("href", ""):
#             target_url = first_result["href"]

#     if not target_url:
#         return None

#     headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
#     }
#     response = requests.get(target_url, headers=headers)
#     if response.status_code != 200:
#         return None
#     soup = BeautifulSoup(response.text, 'html.parser')
#     element = soup.select_one("a:nth-child(2) .ink-700")
#     if element:
#         tmp_text = element.get_text(strip=True)
#         return tmp_text[4:].strip()
#     else:
#         return None
    

