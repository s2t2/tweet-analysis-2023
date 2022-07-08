
# adapted from code by Lucienne Julian (see "notebooks/Tweet_Collector.ipynb")


from datetime import datetime
import os
from pprint import pprint

from dotenv import load_dotenv
from tweepy import Paginator
from pandas import DataFrame, concat

from app.twitter_service import twitter_api_client
from app.tweet_collection.db import CollectionDatabase

load_dotenv()

# https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query#availability
QUERY = os.getenv("QUERY", default="#COP26 lang:en")

START_DATE = os.getenv("START_DATE", default="2022-01-01")
END_DATE = os.getenv("END_DATE", default="2022-01-03")

MAX_RESULTS = int(os.getenv("MAX_RESULTS", default="100")) # per page
PAGE_LIMIT = os.getenv("PAGE_LIMIT") # num of pages max (use only in development)

def fetch_tweets(query=QUERY, start_date=START_DATE, end_date=END_DATE, max_results=MAX_RESULTS, limit=PAGE_LIMIT):
    """
    Params
        query (str) : '#COP26 lang:en'
            see https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query#availability

        start_date (str) : '2022-01-01'

        end_date (str) : '2022-01-03'

        max_results (int) : 100
            (must be less than or equal to 100)
            (maybe for pagination)
            (sometimes we get 99 / less??)

    """
    client = twitter_api_client()

    # start at beginning of day, end at end of day
    formatting_template = '%Y-%m-%d %H:%M:%S'
    start_time = datetime.strptime(f"{start_date} 00:00:00", formatting_template)
    end_time = datetime.strptime(f"{end_date} 23:59:59", formatting_template)

    # https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all
    #return client.search_all_tweets(query=query,
    #    # can't have spaces between the commas ??
    #    expansions=['author_id','attachments.media_keys','referenced_tweets.id','geo.place_id'],
    #    tweet_fields=['created_at','entities','context_annotations'],
    #    media_fields=['url','preview_image_url'],
    #    user_fields=['verified'],
    #    max_results=max_results,
    #    start_time=start_time,
    #    end_time=end_time
    #)

    request_params = dict(
        query=query,
        expansions=[
            'author_id',
            'attachments.media_keys',
            'referenced_tweets.id',
            'referenced_tweets.id.author_id',
            #'in_reply_to_user_id',
            'geo.place_id',
            'entities.mentions.username'
        ],
        tweet_fields=['created_at', 'entities', 'context_annotations'],
        media_fields=['url', 'preview_image_url'],
        user_fields=['verified', 'created_at'],
        max_results=max_results,
        start_time=start_time,
        end_time=end_time
    )
    args = {}
    if limit:
        args["limit"] = int(limit)
    #return Paginator(client.search_all_tweets, limit=limit, **request_params)
    return Paginator(client.search_all_tweets, **args, **request_params)


def process_response(response):
    """
    Param response : tweepy.client.Response
        containing a page of tweets
    """
    tweet_records, tag_records, mention_records, annotation_records = [], [], [], []
    status_media_records = []
    status_entity_records = []

    users = response.includes["users"]
    media = response.includes.get("media") or []
    tweets = response.includes["tweets"]

    #
    # MEDIA
    #[
    #    <Media media_key=3_1543008442390089728 type=photo>,
    #    <Media media_key=7_1543006594677542913 type=video>,
    #    <Media media_key=3_1542997774844788736 type=photo>,
    #    <Media media_key=3_1542982822062858248 type=photo>,
    #    <Media media_key=3_1542982194682941440 type=photo>,
    #    <Media media_key=16_1542982002822901760 type=animated_gif>,
    #    <Media media_key=7_1542966775452733443 type=video>,
    #    <Media media_key=3_1542961753021095942 type=photo>
    #]
    #
    #> 'media_key', 'type', 'url', 'preview_image_url',
    # 'alt_text', 'duration_ms', 'height',  'width',
    # 'non_public_metrics', 'organic_metrics', 'promoted_metrics', 'public_metrics',
    #[
    #    {   'media_key': '16_1542982002822901760',
    #        'preview_image_url': 'https://pbs.twimg.com/tweet_video_thumb/FWnF9N0UcAA9yeW.jpg',
    #        'type': 'animated_gif'
    #    },
    #    {   'media_key': '7_1542966775452733443',
    #        'preview_image_url': 'https://pbs.twimg.com/ext_tw_video_thumb/1542966775452733443/pu/img/Z6xrwhlK54sLoWp9.jpg',
    #        'type': 'video'
    #    },
    #    {
    #        'media_key': '3_1542961753021095942',
    #        'type': 'photo',
    #        'url': 'https://pbs.twimg.com/media/FWmzihbWIAYkQp0.jpg'}]

    media_records = [dict(m) for m in media]
    #print("MEDIA:")
    #pprint(media_records)

    for tweet in response.data:
        user_id = tweet.author_id
        user = [user for user in users if user.id == user_id][0]

        full_text = tweet.text

        retweet_status_id, retweet_user_id = None, None
        reply_status_id, reply_user_id = None, None
        quote_status_id, quote_user_id = None, None

        # sometimes value can be None even if attr is present (WEIRD)
        if hasattr(tweet, "referenced_tweets") and tweet["referenced_tweets"]:
            referenced_tweets = tweet["referenced_tweets"]
            #print("REFS:", len(referenced_tweets))
            for ref in referenced_tweets:
                ref_id = ref.id
                ref_type = ref.type #> "replied_to", "retweeted", "quoted"
                original = [tweet for tweet in tweets if tweet.id == ref_id][0]
                if ref_type == "retweeted":
                    #print("... RT")
                    retweet_status_id = ref_id
                    retweet_user_id = original.author_id
                    full_text = original.text
                elif ref_type == "replied_to":
                    #print("... REPLY")
                    reply_status_id = ref_id
                    reply_user_id = original.author_id
                elif ref_type == "quoted":
                    #print("... QUOTE")
                    quote_status_id = ref_id
                    quote_user_id = original.author_id

        tweet_records.append({
            "status_id": tweet.id,
            "status_text": full_text,
            "created_at": tweet.created_at,
            "user_id": user_id,
            "user_screen_name":user.username,
            "user_name": user.name,
            "user_created_at": user.created_at,
            "user_verified": user.verified,
            "retweet_status_id": retweet_status_id,
            "retweet_user_id": retweet_user_id,
            "reply_status_id": reply_status_id,
            "reply_user_id": reply_user_id,
            "quote_status_id": quote_status_id,
            "quote_user_id": quote_user_id,
        })

        #
        # ENTITIES
        #
        #{   'hashtags': [
        #        {'end': 65, 'start': 45, 'tag': 'January6thCommittee'},
        #        {'end': 178, 'start': 166, 'tag': 'FirstFamily'},
        #        {'end': 198, 'start': 185, 'tag': 'SecondFamily'}
        #    ],
        #    'mentions': [
        #        {'end': 12,'id': '32272710','start': 0,'username': 'Mama4Obama1'},
        #        {'end': 27,'id': '14298769','start': 13,'username': 'MollyJongFast'},
        #        {'end': 151,'id': '1323730225067339784','start': 140,'username': 'WhiteHouse'}
        #    ]
        #    "annotations": [
        #        {'end': 51,'normalized_text': 'Trump','probability': 0.9979,'start': 47,'type': 'Person'},
        #        {'end': 127,'normalized_text': 'Trump','probability': 0.9982,'start': 123,'type': 'Person'}
        #    ]
        #}

        hashtag_entities = tweet.entities.get("hashtags") or []
        tags = [{"status_id": tweet.id, "tag": ent["tag"]} for ent in hashtag_entities]
        #print("TAGS:", tags)
        tag_records += tags

        mention_entities = tweet.entities.get("mentions") or []
        mentions = [{"status_id": tweet.id, "username": ent["username"]} for ent in mention_entities]
        #print("MENTIONS:", mentions)
        mention_records += mentions

        annotation_entities = tweet.entities.get("annotations") or []
        annotations = [{
            "status_id": tweet.id,
            "text": ent["normalized_text"],
            "probability": ent["probability"],
            "type": ent["type"]
        } for ent in annotation_entities]
        #print("ANNOTATIONS:", annotations)
        annotation_records += annotations

        #
        # ATTACHMENTS
        #

        attachments = tweet.attachments
        if attachments:
            #
            # MEDIA
            #
            media_keys = [{"status_id": tweet.id, "media_key": mk} for mk in attachments["media_keys"]]
            #print("MEDIA KEYS:", media_keys)
            status_media_records += media_keys

        #
        # CONTEXT ANNOTATIONS
        #
        #
        # [{'domain': {'description': 'Named people in the world like Nelson Mandela',
        #              'id': '10',
        #              'name': 'Person'},
        #   'entity': {'description': '45th US President, Donald Trump',
        #              'id': '799022225751871488',
        #              'name': 'Donald Trump'}},
        #  {'domain': {'description': 'Politicians in the world, like Joe Biden',
        #              'id': '35',
        #              'name': 'Politician'},
        #   'entity': {'description': '45th US President, Donald Trump',
        #              'id': '799022225751871488',
        #              'name': 'Donald Trump'}},
        #  {'domain': {'description': 'Named people in the world like Nelson Mandela',
        #              'id': '10',
        #              'name': 'Person'},
        #   'entity': {'description': 'Joy Reid',
        #              'id': '872880012436717568',
        #              'name': 'Joy Reid'}},
        #  {'domain': {'description': "A journalist like 'Anderson Cooper'",
        #              'id': '94',
        #              'name': 'Journalist'},
        #   'entity': {'description': 'Joy Reid',
        #              'id': '872880012436717568',
        #              'name': 'Joy Reid'}}]

        if tweet.context_annotations:
            for context_annotation in tweet.context_annotations:
                domain = context_annotation["domain"]
                entity = context_annotation["entity"]
                #entity["domain_id"] = domain["id"]
                #entity["domain_name"] = domain["name"]
                #entity["domain_desc"] = domain["description"]
                #entity["status_id"] = tweet.id
                #status_entity_records.append(entity)
                status_entity_record = {
                    "status_id": tweet.id,
                    "domain_id": domain["id"],
                    "entity_id": entity["id"]
                }
                status_entity_records.append(status_entity_record)



    #return DataFrame(tweet_records)
    return tweet_records, tag_records, mention_records, annotation_records, media_records, status_media_records, status_entity_records




if __name__ == "__main__":

    db = CollectionDatabase()

    page_counter = 0
    for response in fetch_tweets():
        page_counter+=1
        print("PAGE:", page_counter)
        tweets, tags, mentions, annotations, media, status_media, status_entities = process_response(response)
        print("... TWEETS:", len(tweets), "TAGS:", len(tags), "MENTIONS:", len(mentions), "ANNOTATIONS:", len(annotations),
            "MEDIA:", len(media), "STATUS MEDIA:", len(status_media), "STATUS ENTITIES:", len(status_entities),
        )

        db.save_tweets(tweets)
        db.save_tags(tags)
        db.save_mentions(mentions)
        db.save_annotations(annotations)
        db.save_media(media)
        db.save_status_media(status_media)
        db.save_status_entities(status_entities)
