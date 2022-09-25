

import os
import time

from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")
SERVER_NAME = os.getenv("SERVER_NAME", "mjr-local") # the name of your Heroku app (e.g. "impeachment-tweet-analysis-9")

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") # implicit check by google.cloud

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def seek_confirmation():
    if APP_ENV == "development":
        if input("CONTINUE? (Y/N): ").upper() != "Y":
            print("EXITING...")
            exit()

def server_sleep(seconds=None):
    seconds = seconds or (48 * 60 * 60) # 48 hours
    if APP_ENV == "production":
        print(f"SERVER '{SERVER_NAME.upper()}' SLEEPING...")
        time.sleep(seconds)
