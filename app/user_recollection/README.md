# User Recollection


## Setup

Download CSV File of user details (row per unique user, with a "user_id" column to denote the username).

Move it to the "data" folder, at a filepath like: "data/user_recollection/`EVENT_NAME`/`USERS_CSV_FILENAME`"


## Usage

Recollect users to see if they have been suspended or not:

```sh
EVENT_NAME="my_event" USERS_CSV_FILENAME="users.csv" python -m app.user_recollection
```
