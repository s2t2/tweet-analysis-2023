
import os
from functools import cached_property

from app.bq_service import BigQueryService

DATASET_ADDRESS = os.getenv("DATASET_ADDRESS", default="tweet-collector-py.jan6_committee_development") # "MY_PROJECT.MY_DATASET"


class BigQueryDatabase(BigQueryService):

    # NOTE: we do want to use cached properties for the tables...
    # ... however we saw some issues the first time after running migrations
    # ... that the old values were being erroneously referenced
    # ... and the tables were None

    def __init__(self, dataset_address=DATASET_ADDRESS, client=None):
        super().__init__(client=client)
        self.dataset_address = dataset_address.replace(";","") # be safe about sql injection, since we'll be using this address in queries


    @cached_property
    def domains_table(self):
        """consider calling this context_domains"""
        return self.client.get_table(f"{self.dataset_address}.domains")

    @cached_property
    def entities_table(self):
        """consider calling this context_entities"""
        return self.client.get_table(f"{self.dataset_address}.entities")

    @cached_property
    def media_table(self):
        return self.client.get_table(f"{self.dataset_address}.media")

    @cached_property
    def tweets_table(self):
        return self.client.get_table(f"{self.dataset_address}.tweets")

    @cached_property
    def status_annotations_table(self):
        return self.client.get_table(f"{self.dataset_address}.status_annotations")

    @cached_property
    def status_entities_table(self):
        return self.client.get_table(f"{self.dataset_address}.status_entities")

    @cached_property
    def status_media_table(self):
        return self.client.get_table(f"{self.dataset_address}.status_media")

    @cached_property
    def status_mentions_table(self):
        return self.client.get_table(f"{self.dataset_address}.status_mentions")

    @cached_property
    def status_tags_table(self):
        return self.client.get_table(f"{self.dataset_address}.status_tags")

    @cached_property
    def status_urls_table(self):
        return self.client.get_table(f"{self.dataset_address}.status_urls")

    #
    # SAVE RECORDS
    #

    def save_domains(self, records):
        self.insert_records_in_batches(self.domains_table, records)

    def save_entities(self, records):
        self.insert_records_in_batches(self.entities_table, records)

    def save_media(self, records):
        self.insert_records_in_batches(self.media_table, records)

    def save_tweets(self, records):
        self.insert_records_in_batches(self.tweets_table, records)

    def save_status_annotations(self, records):
        self.insert_records_in_batches(self.status_annotations_table, records)

    def save_status_entities(self, records):
        self.insert_records_in_batches(self.status_entities_table, records)

    def save_status_media(self, records):
        self.insert_records_in_batches(self.status_media_table, records)

    def save_status_mentions(self, records):
        self.insert_records_in_batches(self.status_mentions_table, records)

    def save_status_tags(self, records):
        self.insert_records_in_batches(self.status_tags_table, records)

    def save_status_urls(self, records):
        self.insert_records_in_batches(self.status_urls_table, records)

    #
    # MIGRATE TABLES
    # ... https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types
    #

    def migrate_domains_table(self, destructive=False):
        """WARNING! USE WITH EXTREME CAUTION!"""
        sql = ""
        if destructive:
            sql += f"DROP TABLE IF EXISTS `{self.dataset_address}.domains`; "
        sql += f"""
            CREATE TABLE IF NOT EXISTS `{self.dataset_address}.domains` (
                domain_id INT64,
                domain_name STRING,
            );
        """
        self.execute_query(sql)

    def migrate_entities_table(self, destructive=False):
        """WARNING! USE WITH EXTREME CAUTION!"""
        sql = ""
        if destructive:
            sql += f"DROP TABLE IF EXISTS `{self.dataset_address}.entities`; "
        sql += f"""
            CREATE TABLE IF NOT EXISTS `{self.dataset_address}.entities` (
                entity_id INT64,
                entity_name STRING,
                domain_ids ARRAY<INT64>,
            );
        """
        self.execute_query(sql)

    def migrate_media_table(self, destructive=False):
        """WARNING! USE WITH EXTREME CAUTION!"""
        sql = ""
        if destructive:
            sql += f"DROP TABLE IF EXISTS `{self.dataset_address}.media`; "
        sql += f"""
            CREATE TABLE IF NOT EXISTS `{self.dataset_address}.media` (
                media_key STRING,
                type STRING,
                url STRING,
                preview_image_url STRING,

                -- we haven't actually seen these yet
                alt_text STRING,
                duration_ms INT64,
                height INT64,
                width INT64,
            );
        """
        self.execute_query(sql)

    def migrate_tweets_table(self, destructive=False):
        """WARNING! USE WITH EXTREME CAUTION!"""
        sql = ""
        if destructive:
            sql += f"DROP TABLE IF EXISTS `{self.dataset_address}.tweets`; "
        sql += f"""
            CREATE TABLE IF NOT EXISTS `{self.dataset_address}.tweets` (
                status_id INT64,
                status_text STRING,
                created_at TIMESTAMP,

                user_id INT64,
                user_screen_name STRING,
                user_name STRING,
                user_created_at TIMESTAMP,
                user_verified BOOLEAN,

                retweet_status_id INT64,
                retweet_user_id INT64,
                reply_status_id INT64,
                reply_user_id INT64,
                quote_status_id INT64,
                quote_user_id INT64,
            );
        """
        self.execute_query(sql)

    def migrate_status_annotations_table(self, destructive=False):
        """WARNING! USE WITH EXTREME CAUTION!"""
        sql = ""
        if destructive:
            sql += f"DROP TABLE IF EXISTS `{self.dataset_address}.status_annotations`; "
        sql += f"""
            CREATE TABLE IF NOT EXISTS `{self.dataset_address}.status_annotations` (
                status_id INT64,
                type STRING,
                text STRING,
                probability FLOAT64,
            );
        """
        self.execute_query(sql)

    def migrate_status_entities_table(self, destructive=False):
        """WARNING! USE WITH EXTREME CAUTION!"""
        sql = ""
        if destructive:
            sql += f"DROP TABLE IF EXISTS `{self.dataset_address}.status_entities`; "
        sql += f"""
            CREATE TABLE IF NOT EXISTS `{self.dataset_address}.status_entities` (
                status_id INT64,
                domain_id INT64,
                entity_id INT64,
            );
        """
        self.execute_query(sql)

    def migrate_status_media_table(self, destructive=False):
        """WARNING! USE WITH EXTREME CAUTION!"""
        sql = ""
        if destructive:
            sql += f"DROP TABLE IF EXISTS `{self.dataset_address}.status_media`; "
        sql += f"""
            CREATE TABLE IF NOT EXISTS `{self.dataset_address}.status_media` (
                status_id INT64,
                media_key STRING
            );
        """
        self.execute_query(sql)

    def migrate_status_mentions_table(self, destructive=False):
        """WARNING! USE WITH EXTREME CAUTION!"""
        sql = ""
        if destructive:
            sql += f"DROP TABLE IF EXISTS `{self.dataset_address}.status_mentions`; "
        sql += f"""
            CREATE TABLE IF NOT EXISTS `{self.dataset_address}.status_mentions` (
                status_id INT64,
                user_id INT64,
                user_screen_name STRING,
            );
        """
        self.execute_query(sql)

    def migrate_status_tags_table(self, destructive=False):
        """WARNING! USE WITH EXTREME CAUTION!"""
        sql = ""
        if destructive:
            sql += f"DROP TABLE IF EXISTS `{self.dataset_address}.status_tags`; "
        sql += f"""
            CREATE TABLE IF NOT EXISTS `{self.dataset_address}.status_tags` (
                status_id INT64,
                tag STRING,
            );
        """
        self.execute_query(sql)

    def migrate_status_urls_table(self, destructive=False):
        """WARNING! USE WITH EXTREME CAUTION!"""
        sql = ""
        if destructive:
            sql += f"DROP TABLE IF EXISTS `{self.dataset_address}.status_urls`; "
        sql += f"""
            CREATE TABLE IF NOT EXISTS `{self.dataset_address}.status_urls` (
                status_id INT64,
                url STRING,
            );
        """
        self.execute_query(sql)
