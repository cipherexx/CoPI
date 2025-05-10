import json
from gnews import GNews

def getGNews(topic, output_json_path="news.json"):
    '''
    fetches news using the gnews package. It can take
    a good 30-40 seconds and may need to be replaced
    by some other package in the near future that does
    a plug and play with news in json
    '''
    newsFetchObject=GNews()
    response=newsFetchObject.get_news(topic)
    with open(output_json_path, "w") as f:
        json.dump(response, f, indent=2)


'''
TODO:
-->filter responses based on dates to only pick
recent responses
-->explore other functions from gnews for potentially
faster access
'''

