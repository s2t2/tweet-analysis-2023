
# adapted from code by Lucienne Julian (see "notebooks/Tweet_Collector.ipynb")


from datetime import datetime
import os
from pprint import pprint
from types import SimpleNamespace
from functools import cached_property
from uuid import uuid4

from dotenv import load_dotenv
from tweepy import Paginator
from pandas import DataFrame, concat

from app import server_sleep, APP_ENV
from app.twitter_service import twitter_api_client
from app.tweet_collection.db import CollectionDatabase
from app.tweet_collection.bq import BigQueryDatabase

load_dotenv()

STORAGE_MODE = os.getenv("STORAGE_MODE", default="sqlite")

# https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query#availability
QUERY = os.getenv("QUERY", default="#COP26 lang:en")

START_DATE = os.getenv("START_DATE", default="2022-01-01")
END_DATE = os.getenv("END_DATE", default="2022-01-03")

MAX_RESULTS = int(os.getenv("MAX_RESULTS", default="100")) # per page
PAGE_LIMIT = os.getenv("PAGE_LIMIT") # num of pages max (use only in development)

class ParsedResponse(SimpleNamespace):
    def __repr__(self):
        return f"<TweetsResponse size={len(self.tweets)}>"

    @cached_property
    def metrics(self):
        return f"""
            MEDIA: {len(self.media)}
            TWEETS: {len(self.tweets)}
              x ANNOTATIONS: {len(self.status_annotations)}
              x ENTITIES: {len(self.status_entities)}
              x MEDIA: {len(self.status_media)}
              x MENTIONS: {len(self.status_mentions)}
              x TAGS: {len(self.status_tags)}
              x URLS: {len(self.status_urls)}
        """

    @cached_property
    def metrics_log(self):
        return f"... TWEETS: {len(self.tweets)} | MENTIONS: {len(self.status_mentions)} | TAGS: {len(self.status_tags)} | ANNOTATIONS: {len(self.status_annotations)} | URLS: {len(self.status_urls)} | ENTITIES: {len(self.status_entities)} | MEDIA: {len(self.status_media)}"


class Job:
    def __init__(self, storage_mode=STORAGE_MODE, query=QUERY, start_date=START_DATE, end_date=END_DATE, max_results=MAX_RESULTS, page_limit=PAGE_LIMIT):
        self.storage_mode = storage_mode

        if self.storage_mode == "sqlite":
            self.db = CollectionDatabase(destructive=True) # todo: move migration process earlier if desired
        elif self.storage_mode == "bq":
            self.db = BigQueryDatabase()
        else:
            raise AttributeError("oops wrong storage mode")


        self.job_id = str(uuid4())
        self.query = query
        self.start_date = start_date
        self.end_date = end_date
        self.max_results = max_results
        self.page_limit = page_limit

        self.job_start = None
        self.job_end = None
        self.page_counter = 0

        print("------------------")
        print("JOB...")
        print("QUERY:", self.query)
        print("START DATE:", self.start_date)
        print("END DATE:", self.end_date)



    @staticmethod
    def serializable(val):
        if val:
            return str(val)

    @property
    def metadata(self):
        return {
            "job_id": self.job_id,

            "query": self.query,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "max_results": self.max_results,
            "page_limit": self.page_limit,

            "job_start": self.serializable(self.job_start),
            "job_end": self.serializable(self.job_end),
            "page_counter": self.page_counter,
        }


    def fetch_tweets(self):
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
        start_time = datetime.strptime(f"{self.start_date} 00:00:00", formatting_template)
        end_time = datetime.strptime(f"{self.end_date} 23:59:59", formatting_template)

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
            query=self.query,
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
            max_results=self.max_results,
            start_time=start_time,
            end_time=end_time
        )
        args = {}
        if self.page_limit:
            args["limit"] = int(self.page_limit)
        #return Paginator(client.search_all_tweets, limit=limit, **request_params)
        return Paginator(client.search_all_tweets, **args, **request_params)


    def parse_response(self, response):
        """
        Param response : tweepy.client.Response
            containing a page of tweets
        """
        tweet_records, tag_records, mention_records, annotation_records = [], [], [], []
        status_media_records = []
        status_entity_records = []
        url_records = []

        users = response.includes.get("users") or []
        media = response.includes.get("media") or []
        tweets = response.includes.get("tweets") or []

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

        #media_records = [dict(m) for m in media]
        media_records = [{
            "media_key": m["media_key"],
            "type": m["type"],
            "url": m["url"],
            "preview_image_url": m["preview_image_url"],
            # elusive imaginary hypothetical fields?
            "alt_text": m.get("alt_text"),
            "duration_ms": m.get("duration_ms"),
            "height": m.get("height"),
            "width": m.get("width"),
        } for m in media]

        #print("MEDIA:")
        #pprint(media_records)

        if not response.data:
            print("NO RESPONSE DATA!?")
            # or maybe raise?
            return None

        for tweet in response.data:
            user_id = tweet.author_id
            try:
                user = [user for user in users if user.id == user_id][0]
                user_screen_name = user.username
                user_name = user.name
                user_created_at = user.created_at
                user_verified = user.verified
            except IndexError:
                user_screen_name = None
                user_name = None
                user_created_at = None
                user_verified = None

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

                    #original = [tweet for tweet in tweets if tweet.id == ref_id][0]
                    try:
                        original = [tweet for tweet in tweets if tweet.id == ref_id][0]
                    except Exception as err:
                        #print(err, "original tweet not found. will need to look it up later.") #> list index out of range
                        original = None

                    if ref_type == "retweeted":
                        #print("... RT")
                        retweet_status_id = ref_id
                        if original:
                            retweet_user_id = original.author_id
                            full_text = original.text

                        # also get the original tweet's url entities (urls at least)
                        # whether here or in a separate process...
                        # because it requires us to look up the original tweet
                        # we'll do in a separate process so we can look up many original tweets in batches

                    elif ref_type == "replied_to":
                        #print("... REPLY")
                        reply_status_id = ref_id
                        if original:
                            reply_user_id = original.author_id
                    elif ref_type == "quoted":
                        #print("... QUOTE")
                        quote_status_id = ref_id
                        if original:
                            quote_user_id = original.author_id

            tweet_records.append({
                "job_id": self.job_id,
                # tweet info
                "status_id": tweet.id,
                "status_text": full_text,
                "created_at": tweet.created_at,
                # user info
                "user_id": user_id,
                "user_screen_name": user_screen_name,
                "user_name": user_name,
                "user_created_at": user_created_at,
                "user_verified": user_verified,
                #
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

            entities = tweet.entities
            if entities:
                hashtag_entities = entities.get("hashtags") or []
                tags = [{"status_id": tweet.id, "tag": ent["tag"]} for ent in hashtag_entities]
                #print("TAGS:", tags)
                tag_records += tags

                mention_entities = entities.get("mentions") or []
                mentions = [{
                    "status_id": tweet.id,
                    "user_id": ent["id"],
                    "user_screen_name": ent["username"]
                } for ent in mention_entities]
                #print("MENTIONS:", mentions)
                mention_records += mentions

                annotation_entities = entities.get("annotations") or []
                annotations = [{
                    "status_id": tweet.id,
                    "type": ent["type"],
                    "text": ent["normalized_text"],
                    "probability": ent["probability"],
                } for ent in annotation_entities]
                #print("ANNOTATIONS:", annotations)
                annotation_records += annotations

                url_entities = entities.get('urls') or []
                urls = [{
                    'status_id' : tweet.id,
                    'url' : url_ent['expanded_url']
                } for url_ent in url_entities]
                #print("URLS:", urls)
                url_records += urls

            #
            # ATTACHMENTS
            #

            attachments = tweet.attachments
            if attachments:
                #
                # MEDIA
                #
                media_keys = attachments.get("media_keys") or []
                media_keys = [{"status_id": tweet.id, "media_key": mk} for mk in media_keys]
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
        #return tweet_records, tag_records, mention_records, annotation_records, media_records, status_media_records, status_entity_records
        return ParsedResponse(
            media=media_records,
            tweets=tweet_records,
            status_annotations=annotation_records,
            status_entities=status_entity_records,
            status_media=status_media_records,
            status_mentions=mention_records,
            status_tags=tag_records,
            status_urls=url_records
        )


    def perform(self):
        self.job_start = datetime.now()
        self.db.save_job_metadata(self.metadata)

        self.page_counter = 0
        for response in self.fetch_tweets():
            self.page_counter+=1
            print("PAGE:", self.page_counter)
            #tweets, tags, mentions, annotations, media, status_media, status_entities = job.parse_response(response)
            pr = self.parse_response(response)
            if pr:
                #print(pr)
                #print(pr.metrics)
                print(pr.metrics_log)

                self.db.save_tweets(pr.tweets)
                self.db.save_status_tags(pr.status_tags)
                self.db.save_status_mentions(pr.status_mentions)
                self.db.save_status_annotations(pr.status_annotations)
                self.db.save_media(pr.media)
                self.db.save_status_media(pr.status_media)
                self.db.save_status_entities(pr.status_entities)
                self.db.save_status_urls(pr.status_urls)

        self.job_end = datetime.now()
        self.db.update_job_end(self.job_id, str(self.job_end), self.page_counter)


if __name__ == "__main__":

    from app.email_service import send_email
    from app import SERVER_NAME

    job = Job()

    try:
        job.perform()

        if APP_ENV == "production":
            send_email(subject="[Tweet Collection Job Complete]", html=f"""
                <h3>Job Complete!</h3>
                <p>Server Name: <pre>{SERVER_NAME}</pre> </p>
                <p>Job Id: <pre>{job.job_id}</pre> </p>
                <p>Query: <pre>{job.query}</pre> </p>
                <p>Job Metadata: <pre>{job.metadata}</pre> </p>
            """)
    except Exception as err:
        print("OOPS", err)
        if APP_ENV == "production":
            send_email(subject="[Tweet Collection Job Error]", html=f"""
                <h3>Job Error</h3>
                <p>Server Name: <pre>{SERVER_NAME}</pre> </p>
                <p>Job Id: <pre>{job.job_id}</pre> </p>
                <p>Query: <pre>{job.query}</pre> </p>
                <p>Job Error: <pre>{err}</pre> </p>
                <p>Job Metadata: <pre>{job.metadata}</pre> </p>
            """)

    server_sleep()
