


import os

from app.base_db import BaseDatabase

DB_FILEPATH = os.path.join(os.path.dirname(__file__), "tweet_streaming_development.db") # a path to wherever your database exists

TABLE_NAMES = [
    "rules",
    "errors",
    "media", "tweets",
    "status_hashtags", "status_mentions",
    "status_annotations", "status_entities", "status_urls",
    "users", "user_hashtags", "user_mentions"
]

class StreamingDatabase(BaseDatabase):
    def __init__(self, destructive=False, filepath=DB_FILEPATH):
        super().__init__(filepath=filepath, destructive=destructive, table_names=TABLE_NAMES)

    def fetch_rule_names(self):
        results = self.cursor.execute("SELECT DISTINCT rule FROM rules;").fetchall()
        return [row["rule"] for row in results]

    def seed_rules(self, records):
        existing_rules = self.fetch_rule_names()
        new_records = [record for record in records if record["rule"] not in existing_rules]
        self.insert_data("rules", new_records)

    def save_errors(self, records):
        self.insert_data("errors", records)

    def save_media(self, records):
        self.insert_data("media", records)

    def save_tweets(self, records):
        self.insert_data("tweets", records)

    def save_status_hashtags(self, records):
        self.insert_data("status_hashtags", records)

    def save_status_mentions(self, records):
        self.insert_data("status_mentions", records)

    def save_status_media(self, records):
        self.insert_data("status_media", records)

    def save_status_annotations(self, records):
        self.insert_data("status_annotations", records)

    def save_status_entities(self, records):
        self.insert_data("status_entities", records)

    def save_status_urls(self, records):
        self.insert_data("status_urls", records)

    def save_users(self, records):
        self.insert_data("users", records)

    def save_user_hashtags(self, records):
        self.insert_data("user_hashtags", records)

    def save_user_mentions(self, records):
        self.insert_data("user_mentions", records)





if __name__ == "__main__":

    db = StreamingDatabase()
    cursor = db.cursor

    #sql = ""
    #result = cursor.execute(sql).fetchall()
