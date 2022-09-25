
import os
import sqlite3

from pandas import DataFrame

from app import seek_confirmation

#DESTRUCTIVE_MODE = (os.getenv("DESTRUCTIVE_MODE", default="false") == True)


class BaseDatabase:
    """A base interface into SQLite database."""

    def __init__(self, filepath:str, destructive=False, table_names=[]):
        """Params
            filepath (str) : path to the database that will be created
        """
        self.destructive = bool(destructive)

        self.table_names = table_names

        self.filepath = filepath
        print("------------------")
        print("DB FILEPATH:", self.filepath)

        self.connection = sqlite3.connect(self.filepath)
        self.connection.row_factory = sqlite3.Row
        #print("CONNECTION:", self.connection)

        self.cursor = self.connection.cursor()
        #print("CURSOR", self.cursor)

        if self.destructive:
            print("DB DESTRUCTIVE:", self.destructive)
            seek_confirmation()
            self.drop_tables()

    def drop_table(self, table_name):
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name};")

    def drop_tables(self):
        print("DROPPING TABLES:")
        for table_name in self.table_names:
            print("...", table_name)
            self.drop_table(table_name)

    def insert_data(self, table_name:str, records:list):
        """Params:
            table_name (str) : name of table to insert data into
            records (list[dict]) : records to save
        """
        if not records or not any(records):
            return None

        df = DataFrame(records)
        #df.index.rename("row_id", inplace=True) # assigns a column label "id" for the index column
        #df.index += 1 # starts ids at 1 instead of 0
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html
        df.to_sql(table_name, con=self.connection,
            if_exists="append", # append to existing tables (don't throw error)
            #index_label="row_id", # store unique ids for the rows, so we could count them (JK this restarts numbering at 1 for each df)
            index=False
        )
