# CoPI by Mihir Birani
Company Perception Index- a live perception rating for each and every company. Built on completely open and publicly available data, it fetches information about the company in real time and scores it on a variety of factors to give a final perception index.

# Deployment
You can visit CoPI at https://copibymihir.vercel.app

# Working
BeautifulSoup and Selenium based scraper fetch information regarding the following aspects of a company:
1. Financial (Balance Sheet Data fetched from Yahoo Finance!)
2. News (News fetched from Google News)
3. Legal (Court Records fetched by indiankanoon.org)
4. Employee Reviews (Rating directly fetched from AmbitionBox)
5. Customer Reviews (Fetched from Mouthshut)

# Metrics
The final score is based on a weighted average of the above 5 criteria. Precise explanations of the metrics shall be updated here soon. Till then, you can go through the code for reference.
A complete custom-built metric is used to evaluate Financial Performance from balance sheet data, and the news,legal and customer ratings are derived using sentiment analysis on the respective data using separate highly pointed dictionaries. Employee Reviews ae currently a direct reflection of AmbitionBox ratings.
