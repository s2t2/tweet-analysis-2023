
# Media Collection

After you have [collected tweets](../tweet_collection/README.md) and their media, now let's download the media files.

## Setup

This job will save the images locally in the "media" directory.

If you'd like to also upload the images to cloud storage, setup Google Cloud Storage, create a bucket,and demonstrate your ability to connect, as described in the [README](/README.md).


## Usage

```sh
# python -m media_collection.job

# BUCKET_NAME="collection-2022"
# ...
MEDIA_STORAGE_MODE="remote" python -m app.media_collection.job
```
