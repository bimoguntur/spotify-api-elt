import os
from dotenv import load_dotenv

import psycopg2
import logging
import time 

logging.basicConfig(filename='spotify_etl.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv(dotenv_path='./.env')

DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')

MAX_RETRIES = 10
RETRY_DELAY = 2  

def connect():
    attempts = 0
    while attempts < MAX_RETRIES:
        try:
            connection = psycopg2.connect(
                dbname = DB_NAME,
                user = DB_USER,
                password = DB_PASS,
                host =  'spotify_api_db',
                port = '5432'
            )
            return connection
        except psycopg2.Error as e:
            logging.error(f"Error connecting to PostgresSQL: {e}")
            print(f"Error connecting to PostgresSQL: {e}")
            attempts += 1
            time.sleep(RETRY_DELAY)
    raise Exception("Failed to connect to PostgreSQL after multiple attempts")

    

if __name__ == "__main__":
    conn = connect_to_db()
    conn.close()