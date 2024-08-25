import os
from dotenv import load_dotenv
import requests
import logging
import time
from requests.auth import HTTPBasicAuth
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


logging.basicConfig(filename='spotify_etl.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv(dotenv_path='./.env')

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_EMAIL = os.getenv('SPOTIFY_EMAIL')
SPOTIFY_PASSWORD = os.getenv('SPOTIFY_PASSWORD')

DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')


def get_code(scope):
    logging.info("Start Process call get_token function ")
    try: 

        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox  ')
        
        driver = webdriver.Chrome(options=options)
        auth_uri = f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={SPOTIFY_REDIRECT_URI}&scope={scope}"
        print(auth_uri)
        driver.get(auth_uri)

        time.sleep(10)

        username_element = driver.find_element(By.ID, "login-username")
        password_element = driver.find_element(By.ID, "login-password")
        login_button = driver.find_element(By.ID, "login-button")

        username_element.send_keys(SPOTIFY_EMAIL)
        password_element.send_keys(SPOTIFY_PASSWORD)
        login_button.click()

        # time.sleep(10)
        # accept_button = driver.find_element(By.CSS_SELECTOR,"button[data-testid='auth-accept']")
        # accept_button.click()
        time.sleep(4)
        current_url = driver.current_url
        authorization_code = current_url.split('code=')[1]
        driver.quit()
        return authorization_code
    except Exception as e:
        print(f"Error in retrieving code {str(e)}")
        return None

def get_token(use_code, authorization_code):
    url = 'https://accounts.spotify.com/api/token'
    auth = HTTPBasicAuth(SPOTIFY_CLIENT_ID,SPOTIFY_CLIENT_SECRET)
    redirect_uri = SPOTIFY_REDIRECT_URI
    data = {
        'grant_type': 'client_credentials'
    }

    if use_code:
        data['grant_type'] = 'authorization_code'
        data['redirect_uri'] = SPOTIFY_REDIRECT_URI
        data['code'] = authorization_code

    response = requests.post(
        url, auth=auth, data=data
    )

    if response.ok:
        return response.json()
    else:
        print(f"Error retrieving token")
        return None

if __name__ == "__main__":
    scope = 'user-read-recently-played user-top-read'
    code = get_code(scope=scope)
    token = get_token(use_code=True, authorization_code=code)
    with open("auth.json", "w") as outfile:
        outfile.write(json.dumps(token))