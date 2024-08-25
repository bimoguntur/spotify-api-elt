
import requests
from datetime import datetime
from time import time
import os 
from dotenv import load_dotenv
# import pandas as pd
import json
import spotify_api_auth_token 
import db_connection 
import psycopg2

import psycopg2

load_dotenv(dotenv_path='./.env')
DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')


def get_new_releases(token): 
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    url = f"https://api.spotify.com/v1/browse/new-releases"
    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_recently_played(token, after):
    url = "https://api.spotify.com/v1/me/player/recently-played"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    params = {
        "after": after
    }
    response = requests.get(url=url, headers=headers, params=params)
    print(response)
    if response.ok:
        return response.json()
    else:
        return None
    
# def parse_data(json, key):
#     data = json[key]
#     parsed = {
#         'id': [],
#         'title': [],
#         'type': [],
#         'artists': [],
#         'release_date': []
#     }

#     for items in data: 
#         parsed['id'].append(items['id'])
#         parsed['title'].append(items['name'])
#         parsed['type'].append(items['type'])
#         parsed['artists'].append(items['artists'])
#         parsed['release_date'].append(items['release_date'])
        
#         # artists = []
#         # for artist in items["artists"]:
#         #     artists.append(artist["name"])
#         # print(f"{items["type"]} {items["name"]} by {artists} | Release Year {items["release_date"]}")
#     df = pd.DataFrame(parsed, columns=['id', 'title', 'type', 'artists', 'release_date'])
#     pd.set_option('display.width', 2022)
#     print(df)



if __name__ == "__main__":
    token = spotify_api_auth_token.get_token()
    
    connection = db_connection.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT MAX(last_update_unix) FROM last_update")
    rows = cursor.fetchall()

    last_update = ""
    for row in rows:
        last_update = str(row[0])
    
    recently_played = get_recently_played(token=token, after=last_update)

    with open('recently_played.json','w') as output:
        output.write(json.dumps(recently_played))

    page = 0
    while recently_played['next']:
        if len(recently_played['items'])>0:
            total_items = len(recently_played['items'])
            print("Found {total_items} tems, on page {page}. Inserting into table")
            for item in recently_played['items']:

                played_at = datetime.strptime(item['played_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
                id = int(played_at.timestamp())
                track_id = item['track']['id']
                name = item['track']['name'].replace("'","''")
                type = item['track']['type']
                sql = f"""
                    INSERT INTO recently_played (id, track_id, name, type, played_at)
                    VALUES ({id}, '{track_id}', '{name}', '{type}', '{played_at}')
                    ON CONFLICT (id) DO NOTHING
                """
                
                print(sql)
                cursor.execute(sql)
                connection.commit()
                print("Finish inserting to recently_played")
                
        print(f"Found Next Page")
        page+=1
        sql = f"""
            INSERT INTO last_update (last_update_unix)
            VALUES ({recently_played['cursors']['after']})  
            ON CONFLICT (last_update_unix) DO NOTHING          
        """
        
        cursor.execute(sql)
        connection.commit()
        print("Finish inserting to last_update")
        recently_played = get_recently_played(token=token, after=recently_played['cursors']['after'])
        
    cursor.close()
    connection.close()
