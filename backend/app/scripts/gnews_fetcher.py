import json
from pygooglenews import GoogleNews
import pandas as pd
import re
import numpy as np
from statistics import mean
import os
import time


def getNews(topic):
    gn=GoogleNews()
    #time.sleep(0.370975434567898765445678)
    search=gn.search(topic)
    return json.dumps(search)


def analyze_headlines(json_string, lmd_csv_path):
    lmd_df = pd.read_csv(lmd_csv_path, sep=',')
    positive_words = set(lmd_df[lmd_df['Positive'] > 0]['Word'].str.lower())
    negative_words = set(lmd_df[lmd_df['Negative'] > 0]['Word'].str.lower())
    data = json.loads(json_string)
    articles = data.get('entries', [])
    article_list = []
    sentiment_scores = []
    for article in articles:
        title = article.get('title', '')
        link = ''
        if 'links' in article and isinstance(article['links'], list) and len(article['links']) > 0:
            link = article['links'][0].get('href', '')
        elif 'links' in article and isinstance(article['links'], dict):
            link = article['links'].get('href', '')
        elif 'link' in article:
            link = article['link']
        sentiment = analyze_lm_sentiment(title, positive_words, negative_words)
        sentiment_scores.append(sentiment)
        article_list.append({'title': title, 'link': link})
    if sentiment_scores:
        min_score = min(sentiment_scores)
        max_score = max(sentiment_scores)
        
        if max_score - min_score == 0:
            normalized_scores = [5.0] * len(sentiment_scores)
        else:
            normalized_scores = [(s - min_score) / (max_score - min_score) * 10 for s in sentiment_scores]
        rating = np.mean(normalized_scores)
    else:
        rating = 5.0
    output = {
        'rating': round(rating, 2),
        'articles': article_list
    }
    
    return json.dumps(output, indent=2)


def analyze_lm_sentiment(text, positive_words, negative_words):
    words = re.findall(r'\b\w+\b', text.lower())
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    total_sentiment_words = positive_count + negative_count
    if total_sentiment_words > 0:
        lm_polarity = (positive_count - negative_count) / total_sentiment_words
    else:
        lm_polarity = 0
    
    return lm_polarity

def fetch_news_rating(company_name):
    json_string = getNews(company_name)
    script_dir = os.path.dirname(__file__)
    lmd_csv_path = os.path.join(script_dir,'../loughran-mcdonald.csv')
    result = analyze_headlines(json_string, lmd_csv_path)
    return result




