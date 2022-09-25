# Tweet Collection (Search)

## Setup

Setup your twitter credentials, sendgrid credentials, and demonstrate your ability to connect, as described in the [README](/README.md).

Also choose a database (sqlite or bigquery), and if bigquery, run migrations and test your ability to connect, as described in the [README](/README.md).

Migrating tables:

```sh
DATASET_ADDRESS="YOUR_PROJECT.YOUR_DATASET" python -m app.tweet_collection.bq_migrations
```

## Usage

Collect tweets:

```sh
python -m app.tweet_collection.job

# pass custom params:
START_DATE="2022-07-01" END_DATE="2022-07-01" QUERY="lang:en #january6thcommittee" PAGE_LIMIT=3 python -m app.tweet_collection.job

# store to bigquery:
# DATASET_ADDRESS="YOUR_PROJECT.YOUR_DATASET"  ...
STORAGE_MODE="bq" START_DATE="2022-07-01" END_DATE="2022-07-01" QUERY="lang:en #january6thcommittee" PAGE_LIMIT=3 python -m app.tweet_collection.job
```


Collect domains and entities:


```sh
# python -m app.tweet_collection.twitterdev

python -m app.tweet_collection.db_seeds

# DATASET_ADDRESS="YOUR_PROJECT.YOUR_DATASET" ...
python -m app.tweet_collection.bq_seeds
```
