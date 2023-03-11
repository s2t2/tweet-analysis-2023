
import os
from pprint import pprint
#from time import sleep
from datetime import datetime
#from functools import SimpleNamespace, cached_property

from tweepy.streaming import StreamingClient
from tweepy import StreamRule
#from urllib3.exceptions import ProtocolError

from app import seek_confirmation
from app.twitter_service import TWITTER_BEARER_TOKEN
from app.tweet_streaming.storage import get_storage

BATCH_SIZE = int(os.getenv("BATCH_SIZE", default="50"))

class MyClient(StreamingClient):
    """
    The filtered stream deliver Tweets to you in real-time that match on a set of rules.
    Rules are made up of operators that are used to match on a variety of Tweet attributes.
    Multiple rules can be applied to a stream using the POST /tweets/search/stream/rules endpoint.
    Once you've added rules and connect to your stream using the GET /tweets/search/stream endpoint,
        only those Tweets that match your rules will be delivered in real-time through a persistent streaming connection.
        You do not need to disconnect from your stream to add or remove rules.

    See:
        https://docs.tweepy.org/en/stable/streaming.html#using-streamingclient
        https://docs.tweepy.org/en/stable/streamingclient.html#tweepy.StreamingClient

    Data received from the stream is passed to on_data().
    This method handles sending the data to other methods.
        Tweets recieved are sent to on_tweet(),
        includes data are sent to on_includes(),
        errors are sent to on_errors(), and
        matching rules are sent to on_matching_rules().

    A StreamResponse instance containing all four fields is sent to on_response().
    By default, only on_response() logs the data received, at the DEBUG logging level.

    Errors:
        on_closed() is called when the stream is closed by Twitter.
        on_connection_error() is called when the stream encounters a connection error.
        on_request_error() is called when an error is encountered while trying to connect to the stream.
        on_request_error() is also passed the HTTP status code that was encountered.
        The HTTP status codes reference for the Twitter API can be found at https://developer.twitter.com/en/support/twitter-api/error-troubleshooting.
    """

    def __init__(self, bearer_token=TWITTER_BEARER_TOKEN, wait_on_rate_limit=True, batch_size_limit=BATCH_SIZE):
        # todo: also consider passing max_retries
        super().__init__(bearer_token=bearer_token, wait_on_rate_limit=wait_on_rate_limit)

        print("-----------")
        print("STREAMING CLIENT!")
        print("  RUNNING:", self.running)
        print("  SESSION:", self.session)
        print("  THREAD:", self.thread)
        print("  USER AGENT:", self.user_agent)

        # self.add_rules()

        self.storage_mode, self.storage = get_storage()

        self.counter = 0 # refers to the number of responses processed
        self.batch_size_limit = batch_size_limit # refers to the max number of responses in the batch before saving
        self.batch = self.default_batch
        print("-----------")
        print("BATCH SIZE: ", self.batch_size_limit)

        seek_confirmation()


    @property
    def default_batch(self):
        return {
            "errors": [],
            "media": [],
            "tweets": [],
            "status_media": [],
            "status_entities": [],
            "status_hashtags": [],
            "status_mentions": [],
            "status_annotations": [],
            "status_urls": [],
            "users": [],
            "user_hashtags": [],
            "user_mentions": [],
        }

    @property
    def batch_info(self):
        info = {}
        for k, v in self.batch.items():
            info[k] = len(v)
        return info

    @property
    def stream_params(self):
        """
        Expansions: https://developer.twitter.com/en/docs/twitter-api/expansions

        Media Fields: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/media

        Tweet Fields: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet

        User Fields: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/user
        """
        return dict(
            backfill_minutes=5,
            #threaded=False
            expansions=[
                'author_id',
                'attachments.media_keys',
                'referenced_tweets.id', # Returns a Tweet object that this Tweet is referencing (either as a Retweet, Quoted Tweet, or reply)
                'referenced_tweets.id.author_id', # Returns a user object for the author of the referenced Tweet
                'in_reply_to_user_id',
                #'geo.place_id',
                'entities.mentions.username'
            ],
            media_fields=[
                'duration_ms',
                'preview_image_url',
                'public_metrics',
                'width',
                'alt_text',
                'url',
            ],
            #place_fields=[],
            #poll_fields=[],
            tweet_fields=[
                'author_id',
                'context_annotations',
                'conversation_id',
                'created_at',
                'entities',
                'in_reply_to_user_id',
                'lang',
                'public_metrics', #> retweet_count, reply_count, like_count, quote_count
                'referenced_tweets',
                'source'
            ],
            user_fields=[
                'created_at',
                'description',
                #'location',
                'pinned_tweet_id',
                'profile_image_url',
                'public_metrics', #> followers_count, following_count, tweet_count, listed_count
                'entities',
                'url',
                'verified',
            ],
        )

    #
    # DATA PROCESSING
    #

    def on_response(self, response):
        self.counter += 1
        print(self.counter, "---", response.data.id)

        self.parse_response(response)

        if self.counter % self.batch_size_limit == 0:
            self.save_and_clear_batch()

    def save_and_clear_batch(self):
        print("----------------")
        print("SAVING BATCH...")
        pprint(self.batch_info)
        self.storage.save_errors(self.batch["errors"])
        self.storage.save_media(self.batch["media"])
        self.storage.save_tweets(self.batch["tweets"])
        self.storage.save_status_hashtags(self.batch["status_hashtags"])
        self.storage.save_status_mentions(self.batch["status_mentions"])
        self.storage.save_status_media(self.batch["status_media"])
        self.storage.save_status_annotations(self.batch["status_annotations"])
        self.storage.save_status_entities(self.batch["status_entities"])
        self.storage.save_status_urls(self.batch["status_urls"])
        self.storage.save_users(self.batch["users"])
        self.storage.save_user_hashtags(self.batch["user_hashtags"])
        self.storage.save_user_mentions(self.batch["user_mentions"])

        print("------------")
        print("CLEARING BATCH...")
        self.batch = self.default_batch


    def parse_response(self, response):
        # response is a named tuple ("data", "includes", "errors", "matching_rules")

        tweet = response.data
        includes = response.includes
        matching_rules = response.matching_rules
        if any(response.errors):
            print("-----------")
            print("ERRORS...")
            self.parse_errors(response.errors)

        media = response.includes.get("media") or []
        self.parse_media(media)

        ref_tweets = includes.get("tweets") or []
        tweets = [tweet] + ref_tweets
        self.parse_tweets(tweets=tweets, matching_rules=matching_rules)

        users = includes.get("users") or []
        self.parse_users(users)

    def parse_errors(self, errors):
        self.batch["errors"] += [{
            "detail": e["detail"], #> 'User has been suspended: [...].'
            "parameter": e["parameter"], #> entities.mentions.username
            "resource_id": e["resource_id"], #> user screen name
            "resource_type": e["resource_type"], #> user
            "section": e.get("section"), #> includes
            "title": e.get("title"), #> Forbidden
            "type": e.get("type"), #> 'https://api.twitter.com/2/problems/resource-not-found'
            "value": e.get("value"), #> user screen name
        } for e in errors]

    def parse_media(self, media):
        self.batch["media"] += [{
            "media_key": m["media_key"],
            "type": m["type"],
            "url": m["url"],
            "preview_image_url": m["preview_image_url"],
            "alt_text": m.get("alt_text"),
            "duration_ms": m.get("duration_ms"),
            "height": m.get("height"),
            "width": m.get("width"),
        } for m in media]

    def parse_tweets(self, tweets, matching_rules=None):
        matching_rules = matching_rules or []
        matching_rule_ids = [rule.id for rule in matching_rules]
        if self.storage_mode == "sqlite":
            # store flat in sqlite, as lists not supported
            matching_rule_ids = ", ".join(matching_rule_ids)

        for tweet in tweets:

            retweet_status_id, reply_status_id, quote_status_id = None, None, None
            if hasattr(tweet, "referenced_tweets") and tweet["referenced_tweets"]:
                ref_tweets = tweet["referenced_tweets"]
                for ref_tweet in ref_tweets:
                    ref_type = ref_tweet.type #> "replied_to", "retweeted", "quoted"
                    if ref_type == "retweeted":
                        retweet_status_id = ref_tweet.id
                    elif ref_type == "replied_to":
                        reply_status_id = ref_tweet.id
                    elif ref_type == "quoted":
                        quote_status_id = ref_tweet.id

            #breakpoint()
            self.batch["tweets"].append({
                "status_id": tweet.id,
                "status_text": tweet.text,
                "created_at": tweet.created_at,
                "lang": tweet.lang,
                # user info:
                "user_id": tweet.author_id,
                # referenced tweet info:
                "retweet_status_id": retweet_status_id,
                "reply_status_id": reply_status_id,
                "quote_status_id": quote_status_id,
                # this is new
                "conversation_id": tweet.conversation_id,
                # keep track of which rules!
                "matching_rule_ids": matching_rule_ids
            })

            if tweet.attachments:
                media_keys = tweet.attachments.get("media_keys") or []
                media_keys = [{"status_id": tweet.id, "media_key": mk} for mk in media_keys]
                self.batch["status_media"] += media_keys

            if tweet.context_annotations:
                for context_annotation in tweet.context_annotations:
                    domain = context_annotation["domain"]
                    entity = context_annotation["entity"]
                    self.batch["status_entities"].append({
                        "status_id": tweet.id,
                        "domain_id": domain["id"],
                        "entity_id": entity["id"]
                    })

            if tweet.entities:
                hashtag_entities = tweet.entities.get("hashtags") or []
                tags = [{"status_id": tweet.id, "tag": ent["tag"]} for ent in hashtag_entities]
                self.batch["status_hashtags"] += tags

                mention_entities = tweet.entities.get("mentions") or []
                mentions = [{
                    "status_id": tweet.id,
                    "user_id": ent["id"],
                    "user_screen_name": ent["username"]
                } for ent in mention_entities]
                self.batch["status_mentions"] += mentions

                annotation_entities = tweet.entities.get("annotations") or []
                annotations = [{
                    "status_id": tweet.id,
                    "type": ent["type"],
                    "text": ent["normalized_text"],
                    "probability": ent["probability"],
                } for ent in annotation_entities]
                self.batch["status_annotations"] += annotations

                url_entities = tweet.entities.get('urls') or []
                urls = [{
                    'status_id' : tweet.id,
                    'url' : url_ent['expanded_url']
                } for url_ent in url_entities]
                self.batch["status_urls"] += urls

    def parse_users(self, users):
        for user in users:
            self.batch["users"].append({
                "user_id": user.id,
                "screen_name": user.username,
                "name": user.name,
                "description": user.description,
                "url": user.url,
                "profile_image_url": user.profile_image_url,
                "verified": user.verified,
                "created_at": user.created_at,
                "pinned_tweet_id": user.pinned_tweet_id, #> todo: request this
                "followers_count": user.public_metrics["followers_count"],
                "following_count": user.public_metrics["following_count"],
                "tweet_count": user.public_metrics["tweet_count"],
                "listed_count": user.public_metrics["listed_count"],
                "accessed_at": datetime.now(),
            })

            if user.entities:
                profile_entities = user.entities.get("description") or {}
                profile_hashtags = profile_entities.get("hashtags") or []
                profile_mentions = profile_entities.get("mentions") or []

                self.batch["user_hashtags"] += [{
                    "user_id": user.id,
                    "tag": tag["tag"],
                    "accessed_at": datetime.now()
                } for tag in profile_hashtags]

                self.batch["user_mentions"] += [{
                    "user_id": user.id,
                    "mention_screen_name": mention["username"],
                    "accessed_at": datetime.now()
                } for mention in profile_mentions]

    #
    # ERROR HANDLING
    #

    def on_close(self):
        print("-----------")
        print("STREAM ON CLOSE!")
        self.save_and_clear_batch()

    def on_connection_error(self):
        print("-----------")
        print("STREAM ON CONNECTION ERROR!")
        #self.disconnect()
        self.save_and_clear_batch()






if __name__ == "__main__":

    #client = MyClient(TWITTER_BEARER_TOKEN, wait_on_rate_limit=True)
    client = MyClient()

    print("RULES:")
    rules = client.storage.fetch_rule_names()
    stream_rules = [StreamRule(rule) for rule in rules]
    client.add_rules(stream_rules)
    print(client.get_rules())

    # go listen for tweets matching the specified rules
    # https://github.com/tweepy/tweepy/blob/9b636bc529687dbd993bb1aef0177ee78afdabec/tweepy/streaming.py#L553



    # Streams about 1% of all Tweets in real-time.
    #client.sample()
    #client.sample(**stream_params)

    # Streams Tweets in real-time based on a specific set of filter rules.
    #client.filter()
    client.filter(**client.stream_params)
