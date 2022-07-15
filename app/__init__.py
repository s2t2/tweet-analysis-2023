

import os
#import time

from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")

def seek_confirmation():
    if APP_ENV == "development":
        if input("CONTINUE? (Y/N): ").upper() != "Y":
            print("EXITING...")
            exit()

#def server_sleep(seconds=None):
#    seconds = seconds or (6 * 60 * 60) # 6 hours
#    if APP_ENV == "production":
#        print(f"SERVER '{SERVER_NAME.upper()}' SLEEPING...")
#        time.sleep(seconds)
#
