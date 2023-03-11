
import os
from pprint import pprint

from pandas import read_csv

from app import DATA_DIR
from app.tweet_streaming.storage import get_storage

EVENT_NAME = os.getenv("EVENT_NAME", default="my_event")

RULES_CSV_FILEPATH = os.path.join(DATA_DIR, "tweet_streaming", EVENT_NAME, "rules.csv")


if __name__ == "__main__":

    df = read_csv(RULES_CSV_FILEPATH)
    records = df.to_dict("records")
    print("---------------")
    print("RULES (CSV):")
    pprint(records)

    _, storage = get_storage()
    storage.seed_rules(records)
