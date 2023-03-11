# Deploying

Setup the production BigQuery database, and migrate it, using instructions from the README.

Ensure the server has the following env vars:

```sh
APP_ENV="production"
BATCH_SIZE=100
DATASET_ADDRESS="__________.____________"
# GOOGLE CREDENTIALS JSON
STORAGE_MODE="bq"
TWITTER_BEARER_TOKEN="________"
BUCKET_NAME="_____"
```

Deploy.

Turn on the "tweet_streaming_job" process.
