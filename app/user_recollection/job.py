

import os
from functools import cached_property

from dotenv import load_dotenv
from pandas import read_csv, DataFrame

from app.twitter_service import twitter_api_client


load_dotenv()

EVENT_NAME = os.getenv("EVENT_NAME", default="my_event")
USERS_CSV_FILENAME = os.getenv("USERS_CSV_FILENAME", default="user_details_20210806.csv")
USERS_CSV_FILEPATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "user_recollection", EVENT_NAME, USERS_CSV_FILENAME)


class Job:


    def __init__(self, csv_filepath=USERS_CSV_FILEPATH):
        self.csv_filepath = csv_filepath
        print("LOADING USERS FROM CSV:", os.path.abspath(csv_filepath))

        self.client = twitter_api_client()

    @cached_property
    def users_df(self):
        return read_csv(self.csv_filepath)

    @cached_property
    def all_user_ids(self):
        return self.users_df["user_id"].unique().tolist()

    def lookup_users(self, user_ids):
        return self.client.get_users(ids=user_ids)

if __name__ == "__main__":


    job = Job()

    ids_batch = job.all_user_ids[0:100]

    results = job.lookup_users(ids_batch)


    batch = []

    #print("------------")
    #print("SUCCESSES:")
    #success_ids = [user.id for user in results.data]
    #print(len(success_ids)) #>  62

    for user in results.data:
        batch.append({
            "user_id": user.id,
            "error": None,
            "message": None
        })


    #print("------------")
    #print("ERRORS:")
    #error_ids = [err["resource_id"] for err in results.errors]
    #print(len(error_ids))

    for error in results.errors:
        batch.append({
            "user_id": error["resource_id"],
            "error": error["title"], #> 'Not Found Error'
            "message": error["detail"].split(":")[0], #> 'Could not find user with ids: [...].',
        })

        # Forbidden
        #  User has been suspended: [...].

        #print(failure)
        #> {
        #>     'value': '337091850',
        #>     'detail': 'Could not find user with ids: [337091850].',
        #>     'title': 'Not Found Error',
        #>     'resource_type': 'user',
        #>     'parameter': 'ids',
        #>     'resource_id': '337091850',
        #>     'type': 'https://api.twitter.com/2/problems/resource-not-found'
        #> }

    batch_df = DataFrame(batch)
    print(batch_df)

    print(batch_df["error"].value_counts())

    print(batch_df["message"].value_counts())
