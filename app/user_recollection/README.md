# User Recollection


## Setup

Download CSV File of user details (row per unique user, with a "user_id" column to denote the username).

Move it to the "data" folder, at a filepath like: "data/user_recollection/`EVENT_NAME`/`USERS_CSV_FILENAME`"


Migrate new table to store the collection results:

```sql
-- CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_development.recollected_users` (
CREATE TABLE IF NOT EXISTS `tweet-collector-py.impeachment_production.recollected_users` (
    user_id INT64,
    error STRING,
    message STRING,
    lookup_at TIMESTAMP
);
```

## Usage

Recollect users to see if they have been suspended or not:

```sh
EVENT_NAME="my_event" USERS_CSV_FILENAME="users.csv"  python -m app.user_recollection.job

# DATASET_ADDRESS="tweet-collector-py.impeachment_development" EVENT_NAME="impeachment_2020" LIMIT=1000 python -m app.user_recollection.job
```
