
# adapted from code by Lucienne Julian (see "notebooks/Tweet_Collector.ipynb")

import os
from pprint import pprint

from dotenv import load_dotenv
from tweepy import Client
#from pandas import DataFrame

load_dotenv()


TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", default="OOPS")


#class TwitterService:
#    def __init__(self):
#        self.client = Client(bearer_token = TWITTER_BEARER_TOKEN)


def twitter_api_client():
    return Client(bearer_token=TWITTER_BEARER_TOKEN, wait_on_rate_limit=True)

if __name__ == "__main__":

    #client = TwitterService().client
    client = twitter_api_client()

    query = '#COP26 lang:en'

    response = client.search_recent_tweets(query=query,
        # can't have spaces between the commas ??
        expansions=['author_id','attachments.media_keys','referenced_tweets.id','geo.place_id'],
        tweet_fields=['created_at','entities','context_annotations'],
        media_fields=['url','preview_image_url'],
        user_fields=['verified'],
        max_results=100
    )
    tweets = response.data
    print("TWEETS:", len(tweets))
    #for tweet in tweets:
    #    #print(type(tweet)) #> tweepy.tweet.Tweet
    #    print("...", tweet.id, tweet.text)

    print(tweets[0])
    tjs = dict(tweets[0])
    pprint(tjs)
