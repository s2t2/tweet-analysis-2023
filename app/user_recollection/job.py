

import os
from functools import cached_property
from datetime import datetime

from dotenv import load_dotenv
from pandas import read_csv, DataFrame

from app import seek_confirmation
from app.twitter_service import twitter_api_client
from app.bq_service import BigQueryService, DATASET_ADDRESS

load_dotenv()

EVENT_NAME = os.getenv("EVENT_NAME", default="my_event")
USERS_CSV_FILENAME = os.getenv("USERS_CSV_FILENAME", default="user_details_20210806.csv")
USERS_CSV_FILEPATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "user_recollection", EVENT_NAME, USERS_CSV_FILENAME)
LIMIT = os.getenv("LIMIT") # use None as default when we want to run for all users


class Job:

    def __init__(self, csv_filepath=USERS_CSV_FILEPATH, users_limit=LIMIT):
        if users_limit:
            users_limit = int(users_limit)
        self.users_limit = users_limit

        self.csv_filepath = csv_filepath
        print("LOADING USERS FROM CSV:", os.path.abspath(csv_filepath))

        self.client = twitter_api_client()
        self.bq = BigQueryService()
        self.dataset_address = DATASET_ADDRESS
        print("DATASET ADDRESS:", self.dataset_address)

        seek_confirmation()


    @cached_property
    def users_df(self):
        return read_csv(self.csv_filepath)

    @cached_property
    def all_user_ids(self):
        return self.users_df["user_id"].unique().tolist()

    def lookup_users(self, user_ids):
        """Twitter API supports max of 100 users per API call max"""
        return self.client.get_users(ids=user_ids)

    @cached_property
    def recollected_users_table(self):
        return self.bq.client.get_table(f"{self.dataset_address}.recollected_users")

    @cached_property
    def recollected_user_ids(self):
        sql = f"""
            SELECT distinct(user_id) as user_id
            FROM {self.dataset_address}.recollected_users
        """
        #breakpoint()
        #results = list(self.bq.execute_query(sql))
        #return list(self.bq.execute_query(sql))
        df = self.bq.query_to_df(sql)
        if df.empty:
            return []
        else:
            return df["user_id"].tolist()

    def perform(self):
        batch_counter = 1
        recollected_users_table = self.recollected_users_table

        all_ids = self.all_user_ids
        print("ALL:", len(all_ids))

        recollected_user_ids = self.recollected_user_ids
        remaining_user_ids = list(set(all_ids) - set(recollected_user_ids))
        print("REMAINING:", len(remaining_user_ids))

        if self.users_limit:
            remaining_ids = remaining_user_ids[0:self.users_limit]

        for ids_batch in self.bq.split_into_batches(remaining_ids, 100):
            print("BATCH:", batch_counter)

            lookup_at = datetime.now()
            results = self.lookup_users(ids_batch)

            batch = []
            for user in results.data:
                batch.append({
                    "user_id": user.id,
                    "error": None,
                    "message": None,
                    "lookup_at": lookup_at
                })
            for error in results.errors:
                batch.append({
                    "user_id": error["resource_id"],
                    "error": error["title"], #> 'Not Found Error'
                    "message": error["detail"], #.split(":")[0], #> 'Could not find user with ids: [...].',
                    "lookup_at": lookup_at
                })


            self.bq.insert_records_in_batches(recollected_users_table, batch)
            batch_counter +=1



if __name__ == "__main__":


    job = Job()

    job.perform()

    #ids_batch = job.all_user_ids[0:100]
    #
    #results = job.lookup_users(ids_batch)
    #
    #
    #batch = []
    #
    ##print("------------")
    ##print("SUCCESSES:")
    ##success_ids = [user.id for user in results.data]
    ##print(len(success_ids)) #>  62
    #
    #for user in results.data:
    #    batch.append({
    #        "user_id": user.id,
    #        "error": None,
    #        "message": None
    #    })
    #
    #
    ##print("------------")
    ##print("ERRORS:")
    ##error_ids = [err["resource_id"] for err in results.errors]
    ##print(len(error_ids))
    #
    #for error in results.errors:
    #    batch.append({
    #        "user_id": error["resource_id"],
    #        "error": error["title"], #> 'Not Found Error'
    #        "message": error["detail"].split(":")[0], #> 'Could not find user with ids: [...].',
    #    })
    #
    #    # Forbidden
    #    #  User has been suspended: [...].
    #
    #    #print(failure)
    #    #> {
    #    #>     'value': '337091850',
    #    #>     'detail': 'Could not find user with ids: [337091850].',
    #    #>     'title': 'Not Found Error',
    #    #>     'resource_type': 'user',
    #    #>     'parameter': 'ids',
    #    #>     'resource_id': '337091850',
    #    #>     'type': 'https://api.twitter.com/2/problems/resource-not-found'
    #    #> }
    #
    #batch_df = DataFrame(batch)
    #print(batch_df)
    #
    #print(batch_df["error"].value_counts())
    #
    #print(batch_df["message"].value_counts())
    #