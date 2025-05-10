import asyncio
import os
from twikit import Client
from dotenv import load_dotenv
import json

load_dotenv()

USERNAME = os.getenv("TWITTER_USERNAME")
EMAIL = os.getenv("TWITTER_EMAIL")
PASSWORD = os.getenv("TWITTER_PASSWORD")

client = Client('en-IN')

async def fetch_tweets(topic, output_json_path="tweets.json"):
    await client.login(
        auth_info_1=USERNAME,
        auth_info_2=EMAIL,
        password=PASSWORD,
        cookies_file='cookies.json'
    )

    tweets = await client.search_tweet(topic, 'Top', count=100)
    # for tweet in tweets:
    #     print(
    #         tweet.user.name,
    #         tweet.text,
    #         tweet.created_at
    #     )
    tweet_data = []

    for tweet in tweets:
        tweet_data.append({
            "username": tweet.user.name,
            "text": tweet.text,
            "created_at": tweet.created_at.isoformat() if hasattr(tweet.created_at, "isoformat") else str(tweet.created_at)
        })
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(tweet_data, f, ensure_ascii=False, indent=2)
