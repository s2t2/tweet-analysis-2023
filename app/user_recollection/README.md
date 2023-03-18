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

## Monitoring

```sql
WITH results as (
  SELECT
    count(distinct user_id) as lookup_count
    ,count(distinct case when error is null then user_id end) as success_count
    ,count(distinct case when error is not null then user_id end) as failure_count
  FROM `tweet-collector-py.impeachment_production.recollected_users`
)

SELECT *, success_count / lookup_count as success_rate
FROM results
```

## Analysis

```sql
WITH results as (
  SELECT 
    u.opinion_community
    ,u.is_bot
    ,u.is_q
    ,count(distinct ru.user_id) as lookup_count
    ,count(distinct case when ru.error is null then ru.user_id end) as success_count
    ,count(distinct case when ru.error is not null then ru.user_id end) as failure_count
  FROM `tweet-collector-py.impeachment_production.recollected_users` ru
  JOIN `tweet-collector-py.impeachment_production.user_details_v20210806_slim` u ON u.user_id = ru.user_id
  GROUP BY 1,2,3
)

SELECT *, success_count / lookup_count as success_rate
FROM results
ORDER BY 7 DESC
```

For lookups that have failed, it could be due to A) suspension (error message contains "User has been suspended"), or B) either account deletion or switching to private account (error message contains "Could not find user with ids")


```sql
SELECT 
  split(message, ":")[0] as general_error_message
  ,count( distinct user_id) as user_count
FROM `tweet-collector-py.impeachment_production.recollected_users`
WHERE error is not null
GROUP BY 1 
```

```sql
WITH lookups as (
  SELECT 
    ru.user_id
    ,u.opinion_community
    ,u.is_bot
    ,u.is_q
    ,u.avg_fact_score
    ,u.avg_toxicity
    ,ru.error
    ,split(ru.message, ":")[0] as general_message 
  FROM `tweet-collector-py.impeachment_production.recollected_users` ru
  JOIN `tweet-collector-py.impeachment_production.user_details_v20210806_slim` u ON u.user_id = ru.user_id
  -- WHERE error is not null
  --GROUP BY 1, 2,3,4,5
  --LIMIT 10
)

SELECT 
  opinion_community
  ,is_bot
  ,is_q
  ,error
  ,general_message
  ,count(distinct user_id) as user_count
  ,avg(avg_fact_score) as avg_fact_score
  ,avg(avg_toxicity) as avg_toxicity
FROM lookups
GROUP BY 1,2,3,4,5
```

```sql
SELECT 
  *
  , success_count/ lookup_count as success_rate
  ,not_found_count / lookup_count as not_found_rate
  ,suspended_count / lookup_count as suspended_rate
FROM (
  SELECT 
    opinion_community
    ,is_bot
    ,is_q
    --,error
    --,general_message
    ,count(distinct user_id) as lookup_count
    ,count(case when general_message is null then user_id end) as success_count
    ,count(case when general_message = 'Could not find user with ids' then user_id end) as not_found_count
    ,count(case when general_message = 'User has been suspended' then user_id end) as suspended_count
    --,avg(avg_fact_score) as avg_fact_score
    --,avg(avg_toxicity) as avg_toxicity
  FROM (
    SELECT 
      ru.user_id
      ,u.opinion_community
      ,u.is_bot
      ,u.is_q
      ,u.avg_fact_score
      ,u.avg_toxicity
      ,ru.error
      ,split(ru.message, ":")[0] as general_message 
    FROM `tweet-collector-py.impeachment_production.recollected_users` ru
    JOIN `tweet-collector-py.impeachment_production.user_details_v20210806_slim` u ON u.user_id = ru.user_id
  ) lookups
  GROUP BY 1,2,3
)
```



