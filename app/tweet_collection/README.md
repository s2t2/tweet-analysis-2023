# Tweet Collection (2022)

## Setup

You can use a SQLite database, or a BigQuery database. If you want to start with an SQLite database, feel free to skip the BigQuery setup steps below.

### BigQuery Setup

Create two new datasets for each new collection effort. Named `DATASET_ID_development` and `DATASET_ID_production`.


If this is your first time setting up the database, also run the migrations to create the tables:

```sh
# WARNING!!! USE WITH CAUTION!!!
# python -m app.tweet_collection.bq_migrations

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
