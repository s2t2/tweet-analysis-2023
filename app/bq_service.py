import os

from dotenv import load_dotenv
from google.cloud import bigquery
#from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter
from pandas import DataFrame

load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") # implicit check by google.cloud (and keras)


class BigQueryService():

    def __init__(self, client=None):
        self.client = client or bigquery.Client()

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

    service = BigQueryService()
    client = service.client
    print("PROJECT:", client.project)

    print("DATASETS:")
    datasets = list(client.list_datasets())
    for ds in datasets:
        #print("...", ds.project, ds.dataset_id)
        print("...", ds.reference)
