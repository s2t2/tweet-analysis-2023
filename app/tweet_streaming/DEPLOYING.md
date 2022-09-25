



# Deployer's Guide - Tweet Streaming

## Server Setup

Set env vars on the server:

```sh
# (see also tweet collection variables)

# job config:
#heroku config:set BATCH_SIZE="150"
```


## Database Management

Migrate production database:

```sh
DATASET_ADDRESS=________ python -m app.tweet_streaming.bq_migrations
```

Seeding rules:

```sh
DATASET_ADDRESS=________ STORAGE_MODE="remote" python -m app.tweet_streaming.seed_rules
```


## Process Management

Add an entry for the `tweet_streaming_job` to the Procfile (see Procfile).

Setup dyno for the `tweet_streaming_job`.


## Deploying

Deploy / upload code to the server:

```sh
git push heroku main

# git push heroku mybranch:main
```

Viewing the logs:

```sh
heroku logs --tail
```
