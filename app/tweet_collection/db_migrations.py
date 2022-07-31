

from app.tweet_collection.db import CollectionDatabase

if __name__ == "__main__":

    print("DESTRUCTIVE MIGRATIONS")
    db = CollectionDatabase(destructive=True)
    print(db)
