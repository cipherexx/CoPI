import requests
from bs4 import BeautifulSoup
import re
from duckduckgo_search import DDGS
import json

def scrape_rating(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    rating_elements = soup.select(".\\!text-base")
    rating = [el.get_text(strip=True) for el in rating_elements]
    rating=rating[0]
    review_elements = soup.select(".ml-1\\.5")
    reviewcnt = [el.get_text(strip=True) for el in review_elements]
    reviewcnt=extract_review_count(reviewcnt[0])

    return rating,reviewcnt

def extract_review_count(text):
    text = text.lower().strip()
    match = re.search(r'([\d,.]+)\s*([km]?)', text)
    if not match:
        return None
    number, suffix = match.groups()
    number = number.replace(',', '')
    try:
        num = float(number)
        if suffix == 'k':
            num *= 1_000
        elif suffix == 'm':
            num *= 1_000_000
        return int(num)
    except ValueError:
        return None

def get_ambitionbox_rating(company_name, output_json_path="ambitionbox.json"):
    query = f'site:ambitionbox.com "{company_name}" reviews'
    results = DDGS().text(query, max_results=1)
    for result in results:
        url = result.get("href", "")
        if "ambitionbox.com" in url:
            break
    rating,reviewcnt=scrape_rating(url)
    data={
        "rating" : rating,
        "review count" : reviewcnt
    }
    with open(output_json_path, "w") as f:
        json.dump(data, f)

