# https://github.com/s2t2/tweet-analysis-2020/blob/6d1d1691cfb746c2ff06a939ebcf7c4728487cc1/app/gcs_service.py

import os
from functools import cached_property

from google.cloud import storage
from dotenv import load_dotenv

from app import GOOGLE_APPLICATION_CREDENTIALS # implicit check by google-cloud

load_dotenv()

BUCKET_NAME=os.getenv("BUCKET_NAME", default="my-bucket") # "gs://my-bucket"

class GoogleCloudStorageService:
    def __init__(self, bucket_name=BUCKET_NAME):
        self.client = storage.Client() # implicit check for GOOGLE_APPLICATION_CREDENTIALS
        self.bucket_name = bucket_name

        print("CLOUD STORAGE:", self.bucket_name)


    @property
    def metadata(self):
        return {"bucket_name": self.bucket_name}

    @cached_property
    def bucket(self):
        return self.client.bucket(self.bucket_name)

    def upload(self, local_filepath, remote_filepath):
        blob = self.bucket.blob(remote_filepath)

        # avoid timeout errors when uploading a large file
        # h/t: https://github.com/googleapis/python-storage/issues/74
        #
        # https://googleapis.dev/python/storage/latest/blobs.html
        # chunk_size (int) – (Optional) The size of a chunk of data whenever iterating (in bytes).
        # This must be a multiple of 256 KB per the API specification.
        #
        max_chunk_size = 5 * 1024 * 1024  # 5 MB
        blob.chunk_size = max_chunk_size
        blob._MAX_MULTIPART_SIZE = max_chunk_size

        blob.upload_from_filename(local_filepath)
        return blob

    def download(self, remote_filepath, local_filepath):
        blob = self.bucket.blob(remote_filepath)

        ## avoid timeout errors when uploading a large file
        ## h/t: https://github.com/googleapis/python-storage/issues/74
        ##
        ## https://googleapis.dev/python/storage/latest/blobs.html
        ## chunk_size (int) – (Optional) The size of a chunk of data whenever iterating (in bytes).
        ## This must be a multiple of 256 KB per the API specification.
        ##
        #max_chunk_size = 5 * 1024 * 1024  # 5 MB
        #blob.chunk_size = max_chunk_size
        #blob._MAX_MULTIPART_SIZE = max_chunk_size

        blob.download_to_filename(local_filepath)
        return blob


    def file_exists(self, remote_filepath):
        print("FILE EXISTS?", remote_filepath)
        blob = self.bucket.blob(remote_filepath)
        return blob.exists()


if __name__ == "__main__":

    service = GoogleCloudStorageService()

    #print("------------")
    #print("BUCKETS:")
    #for bucket in service.client.list_buckets():
    #    print(bucket)

    print("------------")
    print("BUCKET:")
    bucket = service.bucket
    print(bucket)
