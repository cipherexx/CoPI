import json
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def scrape_indiankanoon(company_name, max_pages, output_path="kanoon.json"):
    current_year = datetime.now().year
    years = [current_year, current_year - 1]
    results = []
    index_counter = 1
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }

    for year in years:
        for page in range(max_pages):
            search_url = f"https://indiankanoon.org/search/?formInput={company_name}%20%20%20doctypes%3A%20judgments%20year%3A%20{year}&pagenum={page}"
            
            try:

                response = requests.get(search_url, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for result in soup.select('.result_title a'):
                    result_title = result.text.strip()
                    result_url = 'https://indiankanoon.org' + result['href']
                    
                    judgment_response = requests.get(result_url, headers=headers)
                    judgment_soup = BeautifulSoup(judgment_response.text, 'html.parser')
                    
                    judgment_content = judgment_soup.select_one('.judgments') or judgment_soup.select_one('.expanded_headline')
                    
                    if judgment_content:
                        content = ' '.join(judgment_content.stripped_strings)
                        results.append({
                            "index": index_counter,
                            "year": year,
                            "headline": result_title,
                            "content": content,
                            "url": result_url
                        })
                        index_counter += 1

            except requests.exceptions.RequestException as e:
                print(f"Error fetching page {page} for {year}: {e}")
                continue

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return len(results)

