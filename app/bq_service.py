import os

from dotenv import load_dotenv
from google.cloud import bigquery
#from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter
from pandas import DataFrame

load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") # implicit check by google.cloud (and keras)


class BigQueryService():
    def __init__(self):
        self.client = bigquery.Client()

    def execute_query(self, sql, verbose=True):
        if verbose == True:
            print(sql)
        job = self.client.query(sql)
        return job.result()

    def query_to_df(self, sql, verbose=True):
        """high-level wrapper to return a DataFrame"""
        results = self.execute_query(sql, verbose=verbose)
        records = [dict(row) for row in list(results)]
        df = DataFrame(records)
        return df


if __name__ == "__main__":
    # only run this code when running this file from the command line
    # ... but NOT when importing code from here

    service = BigQueryService()

    sql = f"""
        SELECT *
        FROM `tweet-research-shared.impeachment_2020.topics`
    """
    df = service.query_to_df(sql)

    print(df.head())
