import json
import time
from time import sleep
from random import randint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def scrape_mouthshut(base_url, num_pages):
    """
    Args:
        base_url (str): Base URL without page number (e.g., 'https://example.com/reviews')
        num_pages (int): Number of pages to scrape

    Returns:
        list: List of review texts
    """
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_experimental_option(
        "prefs", {"profile.default_content_setting_values.notifications": 1}
    )
    chrome_options.page_load_strategy = "eager"
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

    return reviews_list

def get_mouthshut_url(company_name):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.page_load_strategy = "normal"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    formatted_name = company_name.strip().replace(" ", "+")
    search_url = f"https://www.mouthshut.com/search/prodsrch.aspx?data={formatted_name}&type=&p=0"
    driver.get(search_url)
    time.sleep(3)

    try:
        product_link_element = driver.find_element(By.ID, "productRepeater_ctl00_hypProduct")
        product_url = product_link_element.get_attribute("href")
        return product_url
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        driver.quit()

def mouthshut_fetch(company_name, num_pages=1):
    url = get_mouthshut_url(company_name)
    if not url:
        return {"Title": "Mouthshut Review", "Rating": None, "Reviews": []}
    
    reviews = scrape_mouthshut(url, num_pages=num_pages)

    analyzer = SentimentIntensityAnalyzer()
    scores = [analyzer.polarity_scores(review)['compound'] for review in reviews]

    if scores:
        avg_score = sum(scores) / len(scores)
        rating = round((avg_score + 1) * 5, 2) #normalize from [-1,1] to [0,10]
        rating=rating*0.8 #necessary because 20% of the text is companies thanking people
    else:
        rating = None

    return {
        "Title": "Mouthshut Review",
        "Rating": rating,
        "Reviews": reviews
    }
