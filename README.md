# Tweet Analysis 2023

If there is any last minute Twitter data collection we can do before access shuts off, we will do it.


This repo expands upon the [previous approach](https://github.com/s2t2/tweet-analysis-2022), with improvements such as storing the tweet language and matching rule identifiers.


## Installation

Make a copy of this repo. Clone / download your copy of the repo onto your local computer (e.g. the Desktop) then navigate there from the command-line:

```sh
cd ~/Desktop/tweet-analysis-2023
```

Setup a virtual environment:

```sh
conda create -n tweets-2023 python=3.10
```

Activate virtual environment:

```sh
conda activate tweets-2023
```

Install packages:

```sh
pip install -r requirements.txt
```


## Services Setup

### Google Credentials

Create your own Google APIs project, obtain JSON credentials file for a service account, and download it to the root directory of this repo, naming it specifically "google-credentials.json".

### Twitter API Credentials

Obtain Twitter API credentials from the [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard) (i.e. `TWITTER_BEARER_TOKEN` below). Ideally research level access.

### Sendgrid API Credentials

Obtain Sendgrid API credentials from the [Sendgrid website](https://sendgrid.com/) (i.e. `SENDGRID_API_KEY` below). Create a sender identity and verify it (i.e. `SENDER_ADDRESS` below).

### Google Cloud Storage

If you would like to save files to cloud storage, create a new bucket or gain access to an existing bucket, and set the `BUCKET_NAME` environment variable accordingly (see environment variable setup below).


## Database Setup

You can use a SQLite database, or a BigQuery database.

### BigQuery Setup

If you want to use a Bigquery database, in the respective Google APIs project, setup a new BigQuery dataset for each new collection effort. Consider creating two datasets, one for development and one for production.

The `DATASET_ADDRESS` environment variable will be a namespaced combination of the google project name and the dataset name (i.e. "my-project.my_dataset_development").

## Configuration

Create a new local ".env" file and set environment variables to configure services, as desired:

```sh
# this is the ".env" file..

#
# GOOGLE APIS
#
# path to the google credentials file you downloaded
GOOGLE_APPLICATION_CREDENTIALS="/Users/path/to/tweet-analysis-2022/google-credentials.json"

#
# GOOGLE BIGQUERY
#
DATASET_ADDRESS="my-project.my_database_name"

#
# GOOGLE CLOUD STORAGE
#
BUCKET_NAME="my-bucket"

#
# TWITTER API
#
TWITTER_BEARER_TOKEN="..."

#
# SENDGRID API
#
SENDGRID_API_KEY="SG.___________"
SENDER_ADDRESS="example@gmail.com"
```


## Usage

### Services

Demonstrate ability to fetch data from BigQuery, as desired:

```sh
python -m app.bq_service
```

Demonstrate ability to fetch data from Twitter API, as desired:

```sh
python -m app.twitter_service
```

Demonstrate ability to send email, as desired:

```sh
python -m app.email_service
```

Demonstrate ability to connect to cloud storage, as desired:

```sh
python -m app.cloud_storage
```

### Jobs

Search:

  + [Tweet Collection (Search)](app/tweet_collection/README.md)
  + [Media Collection (Search)](app/media_collection/README.md)

Streaming:
  + [Tweet Collection (Streaming)](app/tweet_streaming/README.md)
