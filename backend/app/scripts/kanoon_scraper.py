import json
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def scrape_indiankanoon(company_name, max_pages):
    current_year = datetime.now().year
    years = [current_year, current_year - 1]
    results = []
    index_counter = 1
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    company_name=company_name.replace(" ","+")

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
                            #"content": content,
                            "url": result_url
                        })
                        index_counter += 1

            except requests.exceptions.RequestException as e:
                print(f"Error fetching page {page} for {year}: {e}")
                continue

    # with open(output_path, 'w', encoding='utf-8') as f:
    #     json.dump(results, f, ensure_ascii=False, indent=2)
    return json.dumps(results, ensure_ascii=True, indent=2)

def clamp(value, min_value, max_value):
  return max(min_value, min(value, max_value))

def indiankanoon_metric(company_name):
    '''
    METRIC:
        if no cases: full 10(ensure the page loaded though)
        1. HCSCP: 1-((cases in hc or sc)/(total cases)) [for all cases over last 2 years] = 1-(hsc/(xc+xp))
        2. YCGR: 1/2*(1-clamp((this year*(12/(current_month)) - last year)/last year),-1,1) = 0.5*(1-clamp((xc*12/current_month-xp)/xp),-1,1)
        3. Final : 10*HCSCP*YCGR

    Required values:
    1. xc=cases this year
    2. xp = cases last year
    3. current_month
    4. hsc=cases in high court or supreme court over last 2 years
    '''
    current_year=datetime.now().year
    current_month=datetime.now().month
    company_name=company_name.replace(" ","+")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    xc_url = f"https://indiankanoon.org/search/?formInput={company_name}%20%20%20doctypes%3A%20judgments%20year%3A%20{current_year}"
    xp_url = f"https://indiankanoon.org/search/?formInput={company_name}%20%20%20doctypes%3A%20judgments%20year%3A%20{current_year-1}"
    hsc1_url=f"https://indiankanoon.org/search/?formInput={company_name}%20%20%20%20%20%20%20doctypes%3A%20highcourts%2Csc+year:{current_year}"
    hsc2_url=f"https://indiankanoon.org/search/?formInput={company_name}%20%20%20%20%20%20%20doctypes%3A%20highcourts%2Csc+year:{current_year-1}"
    try:
        response = requests.get(xc_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        xc = None
        for result in soup.select('#search-form+ div b'):
            xc=result.text.split("of")[1].strip()
        if not xc:
            for result in soup.select('.didyoumean + div b'):
                xc=result.text.split("of")[1].strip()
        response = requests.get(xp_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        xc=int(xc)
        xp = None
        for result in soup.select('#search-form+ div b'):
            xp=result.text.split("of")[1].strip()
        if not xp:
            for result in soup.select('.didyoumean + div b'):
                xp=result.text.split("of")[1].strip()
        response = requests.get(hsc1_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        xp=int(xp)
        hsc1 = None
        for result in soup.select('#search-form+ div b'):
            hsc1=result.text.split("of")[1].strip()
        if not hsc1:
            for result in soup.select('.didyoumean + div b'):
                hsc1=result.text.split("of")[1].strip()
        response = requests.get(hsc2_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        hsc1=int(hsc1)
        hsc2 = None
        for result in soup.select('#search-form+ div b'):
            hsc2=result.text.split("of")[1].strip()
        if not hsc2:
            for result in soup.select('.didyoumean + div b'):
                hsc2=result.text.split("of")[1].strip()
        hsc2=int(hsc2)
        hsc=hsc1+hsc2
        HCSCP=clamp((1-(hsc/(xp+xc))), 0.01,10)
        YCGR=0.5*(1-clamp(((xc*12/current_month-xp)/xp),-1,1))
        return 10*HCSCP*YCGR
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page : {e}")

def fetch_indiankanoon_final(company_name):
    rating=indiankanoon_metric(company_name)
    company_name=company_name.replace(" ","+")
    url="https://indiankanoon.org/search/?formInput={company_name}"
    #content=scrape_indiankanoon(company_name,1)
    result={
        "rating" : rating,
       # "articles" : content,
       "url" : url
    }
    return json.dumps(result)

        
        
        
        






