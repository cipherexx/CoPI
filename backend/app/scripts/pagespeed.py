import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def fetchPSAnalyticsInternal(url, output_path="ps_analytics.json", strategy='mobile'):
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
        #print(f"Saved PageSpeed data to: {output_path}")
    else:
        print(f"API request failed. Status: {response.status_code}")
        print(f"Response: {response.text}")
        raise Exception("Failed to fetch PageSpeed data.")



from duckduckgo_search import DDGS
from urllib.parse import urlparse
import tldextract
from thefuzz import fuzz

def get_company_homepage(company_name, min_similarity=80):
    query = f"{company_name} official website india"
    name_key = company_name.lower().replace(" ", "")

    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=8)
        for r in results:
            url = r.get("href") or r.get("url")
            if not url:
                continue
            ext = tldextract.extract(url)
            domain_name = ext.domain.lower()
            similarity = fuzz.partial_ratio(name_key, domain_name)
            if similarity >= min_similarity:
                return url
    return None



def fetchPSAnalytics(company_name, output_path="ps_analytics.json", strategy='mobile'):
    homepage = get_company_homepage(company_name)
    if not homepage:
        return
    fetchPSAnalyticsInternal(homepage, output_path=output_path, strategy='mobile')

