# Tweet Analysis 2022


## Installation

### Repo Setup

Make a copy of this template repo. Clone / download your copy of the repo onto your local computer (e.g. the Desktop) then navigate there from the command-line:

```sh
cd ~/Desktop/tweet-analysis-2022
```

Setup a virtual environment:

```sh
conda create -n tweets-2022 python=3.10
```

Active virtual environment:

```sh
conda activate tweets-2022
```

Install packages:

```sh
pip install -r requirements.txt
```


## Setup

### Google Credentials

Create your own Google APIs project, obtain JSON credentials file for a service account, and download it to the root directory of this repo, naming it specifically "google-credentials.json".

### Twitter API Credentials

Obtain Twitter API credentials from the [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard) (i.e. `TWITTER_BEARER_TOKEN` below). Ideally research level access.

### Sendgrid API Credentials

Obtain Sendgrid API credentials from the [Sendgrid website](https://sendgrid.com/) (i.e. `SENDGRID_API_KEY` below). Create a sender identity and verify it (i.e. `SENDER_ADDRESS` below).


### Environment Variables

Create a new local ".env" file and set the following environment variable (`GOOGLE_APPLICATION_CREDENTIALS`):

```sh
# this is the ".env" file..

# path to the google credentials file you downloaded
GOOGLE_APPLICATION_CREDENTIALS="/Users/YOUR_USERNAME/Desktop/tweet-analysis-2022/google-credentials.json"


TWITTER_BEARER_TOKEN="..."


SENDGRID_API_KEY="SG.___________"
SENDER_ADDRESS="example@gmail.com"

```

## Usage


Demonstrate ability to fetch data from BigQuery:

```sh
python -m app.bq_service
```

Demonstrate ability to fetch data from Twitter API:

```sh
python -m app.twitter_service
```

Demonstrate ability to send email:

```sh
python -m app.email_service
```
