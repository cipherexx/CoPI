import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def fetchPSAnalytics(url, output_path="ps_analytics.json", strategy='mobile'):
    """
    Fetch PageSpeed Insights results and save them to a JSON file.
    """
    api_key = os.getenv('gcp_pagespeed_api')
    if not api_key:
        raise EnvironmentError("API key not found. Set it in a .env file or system environment variable.")

    endpoint = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        'url': url,
        'strategy': strategy,
        'key': api_key
    }

    headers = {
        'User-Agent': ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/114.0.0.0 Safari/537.36")
    }

    response = requests.get(endpoint, params=params, headers=headers)

    if response.status_code == 200:
        with open(output_path, 'w') as f:
            json.dump(response.json(), f, indent=2)
        print(f"Saved PageSpeed data to: {output_path}")
    else:
        print(f"API request failed. Status: {response.status_code}")
        print(f"Response: {response.text}")
        raise Exception("Failed to fetch PageSpeed data.")
