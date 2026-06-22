#Will be the database file for Stock Scrubber

import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()



#Get the url used to talk to the database
def get_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))