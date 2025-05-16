import wikipedia
import requests
from bs4 import BeautifulSoup

def retrieve_logo(company_name):
    results=wikipedia.search(company_name)
    print(results[0])
    # page=wikipedia.page(results[0])
    # print(page.url)
    base=results[0].replace(" ","_")
    url=f"https://en.wikipedia.org/wiki/{base}"
    print(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    ans=None
    for result in soup.select('.logo .mw-file-element'):
        ans=result['src']
    try:
        if not ans or 'svg' not in ans:
            results=soup.select('tr:nth-child(1) .mw-file-element')
            ans=results[0]['src']
    except:
        pass
    try:
        if not ans or 'svg' not in ans:
            results = soup.select('tr:first-child img')
            ans=results[0]['src']
    except:
        pass
    if ans:
        ans=f"https:{ans}"
        return ans
    return None