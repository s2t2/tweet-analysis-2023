
# Tweet Collection (Stream Listener)

Adapted from [previous approach](https://github.com/s2t2/tweet-analysis-2020/tree/main/app/tweet_collection_v2), updated for Twitter API v2 (Tweepy package v4).

## Setup

Setup your Twitter credentials, and demonstrate your ability to connect, as described in the [README](/README.md).

Choose a database (SQLite or BigQuery), and if BigQuery, test your ability to connect, as described in the [README](/README.md).

### Database Migrations

BigQuery Migration:

```sh
DATASET_ADDRESS="YOUR_PROJECT.YOUR_DATASET" python -m app.tweet_streaming.bq_migrations
```

There is no need to migrate the SQLite database.

### Streaming Rules

   + https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule
   + https://docs.tweepy.org/en/stable/streamrule.html#tweepy.StreamRule
   + https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/post-tweets-search-stream-rules

 All operators are evaluated in a case-insensitive manner. For example, the rule cat will match all of the following: cat, CAT, Cat.

 EXAMPLES:
   + `#MyTag`
   + `"twitter data" has:mentions (has:media OR has:links)` ...
   + `snow day #NoSchool` ... will match Tweets containing the terms snow and day and the hashtag #NoSchool.
   + `grumpy OR cat OR #meme` will match any Tweets containing at least the terms grumpy or cat, or the hashtag #meme.
   + `cat #meme -grumpy` ... will match Tweets containing the hashtag #meme and the term cat, but only if they do not contain the term grumpy.
   + `(grumpy cat) OR (#meme has:images)` ... will return either Tweets containing the terms grumpy and cat, or Tweets with images containing the hashtag #meme. Note that ANDs are applied first, then ORs are applied.


### Database Seeds (Adding Rules)

Make a directory in the "data/tweet_streaming" directory with a name representing your own `EVENT_NAME` (e.g. "jan6_committee"). In it create a "rules.csv" file with contents like:

    rule
    #Jan6Committee lang:en
    #January6Committe lang:en
    etc...


> FYI: the first row "rule" is a required column header

Seed your chosen database with rules from the CSV file:

```sh
# for SQLite:
STORAGE_MODE="local" python -m app.tweet_streaming.seed_rules
# EVENT_NAME="YOUR_EVENT" python -m app.tweet_streaming.seed_rules

# for BigQuery:
STORAGE_MODE="remote" DATASET_ADDRESS="YOUR_PROJECT.YOUR_DATASET" python -m app.tweet_streaming.seed_rules
#EVENT_NAME="YOUR_EVENT" DATASET_ADDRESS="YOUR_PROJECT.YOUR_DATASET" python -m app.tweet_streaming.seed_rules
```

UPDATE: we found that rules are associated with the bearer token, and so if you have added a rule by accident, you can run the rules manager to delete it by its identifier:


```sh
python -m app.tweet_streaming.rules_manager
```

## Usage

Collect tweets matching the specified stream rules:

```sh
python app.tweet_streaming.job

# with batch size:
BATCH_SIZE=5 python app.tweet_streaming.job

# storing to SQLite:
STORAGE_MODE="local" python app.tweet_streaming.job

# storing to BigQuery:
STORAGE_MODE="remote" DATASET_ADDRESS="YOUR_PROJECT.YOUR_DATASET" python app.tweet_streaming.job
```
