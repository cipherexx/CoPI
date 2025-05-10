import json
from time import sleep
from random import randint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from googlesearch import search

def scrape_mouthshut(base_url, num_pages, output_json_path="mouthshut.json"):
    """
    Args:
        base_url (str): Base URL without page number (e.g., 'https://example.com/reviews')
        num_pages (int): Number of pages to scrape
        output_json_path (str): Path for output JSON file
    """
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_experimental_option(
        "prefs", {"profile.default_content_setting_values.notifications": 1}
    )
    chrome_options.add_argument("--headless=new")

    # Initialize WebDriver with automatic ChromeDriver management
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    reviews_list = []

    try:
        for page in range(1, num_pages + 1):
            current_url = f"{base_url}-page-{page}"
            driver.get(current_url)
            sleep(randint(1, 3))  # Randomized delay between requests

            # Expand all "Read More" sections
            try:
                read_more_buttons = driver.find_elements(By.LINK_TEXT, 'Read More')
                for button in read_more_buttons:
                    button.click()
                    sleep(0.2)
            except Exception as e:
                print(f"Error expanding content on page {page}: {str(e)}")

            # Parse page content
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            review_containers = soup.find_all('div', class_='row review-article')

            # Extract review text
            for container in review_containers:
                review_content = container.find('div', class_='more reviewdata')
                if review_content and review_content.text.strip():
                    reviews_list.append(review_content.text.strip())

            print(f"Processed page {page}/{num_pages}")

    except Exception as e:
        print(f"Scraping interrupted: {str(e)}")
    finally:
        driver.quit()

    # Index reviews
    indexed_reviews = [{"index": i+1, "review": review} for i, review in enumerate(reviews_list)]

    # Save results to JSON
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(indexed_reviews, json_file, ensure_ascii=False, indent=2)
    
    print(f"Successfully saved {len(indexed_reviews)} reviews to {output_json_path}")

def get_mouthshut_url(company_name, num_results=5):
    query = f'site:mouthshut.com "{company_name}"'
    for result in search(query, num_results=num_results):
        if "mouthshut.com" in result:
            return result
    return None

# #Example Usage
# from mouthshut_scraper import scrape_mouthshut, get_mouthshut_url
# scrape_mouthshut(get_mouthshut_url("blinkit"), 2)

