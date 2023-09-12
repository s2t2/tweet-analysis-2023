## Data Warehouse Migrations

Copying data into the shared environment, for analysis:

```sql
-- DROP TABLE IF EXISTS `tweet-research-shared.f1_racing_2023.streaming_rules`;
CREATE TABLE IF NOT EXISTS `tweet-research-shared.f1_racing_2023.streaming_rules` as (
  SELECT *
  FROM `tweet-collector-py.f1_racing_2023_production.streaming_rules`
);

-- DROP TABLE IF EXISTS `tweet-research-shared.f1_racing_2023.streaming_tweets`;
CREATE TABLE IF NOT EXISTS `tweet-research-shared.f1_racing_2023.streaming_tweets` as (
  SELECT *
  FROM `tweet-collector-py.f1_racing_2023_production.streaming_tweets`
);

-- DROP TABLE IF EXISTS `tweet-research-shared.f1_racing_2023.streaming_users`;
CREATE TABLE IF NOT EXISTS `tweet-research-shared.f1_racing_2023.streaming_users` as (
  SELECT *
  FROM `tweet-collector-py.f1_racing_2023_production.streaming_users`
);


-- DROP TABLE IF EXISTS `tweet-research-shared.f1_racing_2023.streaming_status_annotations`;
CREATE TABLE IF NOT EXISTS `tweet-research-shared.f1_racing_2023.streaming_status_annotations` as (
  SELECT *
  FROM `tweet-collector-py.f1_racing_2023_production.streaming_status_annotations`
);

-- DROP TABLE IF EXISTS `tweet-research-shared.f1_racing_2023.streaming_status_entities`;
CREATE TABLE IF NOT EXISTS `tweet-research-shared.f1_racing_2023.streaming_status_entities` as (
  SELECT *
  FROM `tweet-collector-py.f1_racing_2023_production.streaming_status_entities`
);

-- DROP TABLE IF EXISTS `tweet-research-shared.f1_racing_2023.streaming_status_hashtags`;
CREATE TABLE IF NOT EXISTS `tweet-research-shared.f1_racing_2023.streaming_status_hashtags` as (
  SELECT *
  FROM `tweet-collector-py.f1_racing_2023_production.streaming_status_hashtags`
);

-- DROP TABLE IF EXISTS `tweet-research-shared.f1_racing_2023.streaming_media`;
CREATE TABLE IF NOT EXISTS `tweet-research-shared.f1_racing_2023.streaming_media` as (
  SELECT *
  FROM `tweet-collector-py.f1_racing_2023_production.streaming_media`
);

-- DROP TABLE IF EXISTS `tweet-research-shared.f1_racing_2023.streaming_status_mentions`;
CREATE TABLE IF NOT EXISTS `tweet-research-shared.f1_racing_2023.streaming_status_mentions` as (
  SELECT *
  FROM `tweet-collector-py.f1_racing_2023_production.streaming_status_mentions`
);

-- DROP TABLE IF EXISTS `tweet-research-shared.f1_racing_2023.streaming_status_urls`;
CREATE TABLE IF NOT EXISTS `tweet-research-shared.f1_racing_2023.streaming_status_urls` as (
  SELECT *
  FROM `tweet-collector-py.f1_racing_2023_production.streaming_status_urls`
);

-- DROP TABLE IF EXISTS `tweet-research-shared.f1_racing_2023.streaming_user_hashtags`;
CREATE TABLE IF NOT EXISTS `tweet-research-shared.f1_racing_2023.streaming_user_hashtags` as (
  SELECT *
  FROM `tweet-collector-py.f1_racing_2023_production.streaming_user_hashtags`
);


-- DROP TABLE IF EXISTS `tweet-research-shared.f1_racing_2023.streaming_user_mentions`;
CREATE TABLE IF NOT EXISTS `tweet-research-shared.f1_racing_2023.streaming_user_mentions` as (
  SELECT *
  FROM `tweet-collector-py.f1_racing_2023_production.streaming_user_mentions`
);
```
