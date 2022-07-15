



# Deployer's Guide - Tweet Collection

NOTES IN PROGRESS


Set env vars on the server:

```sh
# storage config:
heroku config:set STORAGE_MODE="bq"
heroku config:set DATASET_ADDRESS="YOUR_PROJECT.YOUR_DATASET"

# job config:
heroku config:set START_DATE="2022-07-01"
heroku config:set END_DATE="2022-07-01"
heroku config:set QUERY="lang:en #january6thcommittee"
```

todo: add to Procfile:

```sh
tweet_collection_job: python -m app.tweet_collection.job
```

Setup dyno for the `tweet_collection_job`.
