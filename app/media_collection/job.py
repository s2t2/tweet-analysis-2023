



import os
#from uuid import uuid4

from dotenv import load_dotenv
import requests

from app import seek_confirmation
from app.cloud_storage import GoogleCloudStorageService
from app.tweet_collection.job import STORAGE_MODE #, Job
from app.tweet_collection.db import CollectionDatabase
#from app.tweet_collection.bq import BigQueryDatabase

load_dotenv()

MEDIA_STORAGE_MODE = os.getenv("MEDIA_STORAGE_MODE", default="local")

MEDIA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "media")

class Job:
    def __init__(self, storage_mode=STORAGE_MODE, media_storage_mode=MEDIA_STORAGE_MODE, media_limit=None):
        self.storage_mode = storage_mode
        if self.storage_mode == "sqlite":
            self.db = CollectionDatabase(destructive=False)
        #elif self.storage_mode == "bq":
        #    self.db = BigQueryDatabase()
        else:
            raise AttributeError("oops wrong storage mode")

        self.media_storage_mode = media_storage_mode.lower()
        if self.media_storage_mode == "local":
            self.media_store = None
        elif self.media_storage_mode in ["gcs", "remote", "cloud_storage"]:
            self.media_store = GoogleCloudStorageService()
        # maybe consider AWS if you like that kind of thing
        else:
            raise AttributeError("oops wrong media storage mode")

        print("------------------")
        print("MEDIA COLLECTION JOB...")

        print()
        seek_confirmation()


    def download_media(self, url, local_filepath):
        response = requests.get(url)
        with open(local_filepath, "wb") as media_file:
            media_file.write(response.content)

    def perform(self):
        for row in self.db.get_downloadable_media():
            media_key = row["media_key"]
            media_type = row["media_type"]
            media_url = row["media_url"]
            preview_url = row["preview_image_url"]

            print(f"{media_type.upper()} {media_key}...")

            if media_url:
                filename = f"{media_key}.jpg"
                self.process_media(media_key=media_key, media_url=media_url, filename=filename)

            if preview_url:
                filename = f"{media_key}_preview.jpg"
                self.process_media(media_key=media_key, media_url=preview_url, filename=filename)


    def process_media(self, media_key, media_url, filename=None):
        filename = filename or f"{media_key}.jpg"
        print("... DOWNLOADING ...", filename)

        local_filepath = os.path.join(MEDIA_DIR, filename)
        self.download_media(url=media_url, local_filepath=local_filepath)

        if self.media_store:
            remote_filepath = os.path.join("media", filename)
            print("... UPLOADING ...", remote_filepath)
            self.media_store.upload(local_filepath=local_filepath, remote_filepath=remote_filepath)


if __name__ == "__main__":


    job = Job()

    job.perform()
