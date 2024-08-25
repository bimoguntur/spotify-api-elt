import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

load_dotenv(dotenv_path='./.env')
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REFRESH_TOKEN = os.getenv('SPOTIFY_REFRESH_TOKEN')

DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')

def get_token():
    url = 'https://accounts.spotify.com/api/token'
    auth = HTTPBasicAuth(SPOTIFY_CLIENT_ID,SPOTIFY_CLIENT_SECRET)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': SPOTIFY_REFRESH_TOKEN
    }

    response = requests.post(
        url, auth=auth, data=data, headers=headers
    )
    
    if response.ok:
        return response.json()['access_token']
    else:
        print(f"Error retrieving token")
        return None
    
if __name__ == "__main__":
    token = get_token()
    print(token)