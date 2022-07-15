

from app import seek_confirmation
from app.tweet_collection.bq import BigQueryDatabase


if __name__ == "__main__":

    db = BigQueryDatabase()
    print("DB:", db.dataset_address.upper())

    print("THIS SCRIPT WILL DESTRUCTIVELY MIGRATE TABLES")
    seek_confirmation()

    #db.migrate_entities_table(destructive=True)
    db.migrate_media_table(destructive=True)
    db.migrate_tweets_table(destructive=True)
    db.migrate_status_annotations_table(destructive=True)
    db.migrate_status_entities_table(destructive=True)
    db.migrate_status_media_table(destructive=True)
    db.migrate_status_mentions_table(destructive=True)
    db.migrate_status_tags_table(destructive=True)
    db.migrate_status_urls_table(destructive=True)
