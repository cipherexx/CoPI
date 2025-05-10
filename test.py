# import pagespeed
# from pagespeed import fetchPSAnalytics

# fetchPSAnalytics("https://www.cipherexx.github.io")

# from gnews_fetcher import getGNews
# getGNews(topic="schools")

# from yfinance_fetcher import build_perception_json
# nse_input = "SWIGGY"
# bse_input = None

# output_json = build_perception_json(nse_input, bse_input)
# print(output_json)

import asyncio
from twikit_fetcher import fetch_tweets
asyncio.run(fetch_tweets("swiggy"))