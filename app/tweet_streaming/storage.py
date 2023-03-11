

import os

from app.tweet_streaming.db import StreamingDatabase
from app.tweet_streaming.bq import BigQueryDatabase


STORAGE_MODE = os.getenv("STORAGE_MODE", default="local")


def get_storage(storage_mode=STORAGE_MODE):
    if storage_mode in ["local", "sqlite", "db"]:
        return "sqlite", StreamingDatabase()
    elif storage_mode in ["remote", "bq"]:
        return "bq", BigQueryDatabase()
