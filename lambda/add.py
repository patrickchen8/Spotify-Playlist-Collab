import requests 
import os 
import json 
import datatier
from configparser import ConfigParser
from utils import * 

def lambda_handler(event, context):
    try:
        config_file = 'config.ini'
        os.environ['CREDENTIALS'] = config_file 

        configur = ConfigParser()
        configur.read(config_file)

        #Spotify 
        client_id = configur.get('spotify', 'client_id')
        client_secret = configur.get('spotify', 'client_secret')
        playlist_id = configur.get('spotify', 'playlist_id')

        #RDS
        rds_endpoint = configur.get('rds', 'endpoint')
        rds_portnum = int(configur.get('rds', 'port_number'))
        rds_username = configur.get('rds', 'user_name')
        rds_pwd = configur.get('rds', 'user_pwd')
        rds_dbname = configur.get('rds', 'db_name')
        dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

        

        print('-----GETTING TOKEN--------')
        #
        # get authentication token from the request 
        #
        if "headers" not in event:
            msg = "no headers in request"
            print("**ERROR:", msg)
            return {
            'statusCode': 400,
            'body': json.dumps(msg)
            }
        headers = event["headers"]
        
        if "Authentication" not in headers:
            msg = "no security credentials"
            print("**ERROR:", msg)
            return {
            'statusCode': 400,
            'body': json.dumps(msg)
            }
            
        print('A')
        token = headers["Authentication"]
            
        if token is None:
            return {
                'statusCode': 400,
                'body': 'Authorization Token Required'
            }
        
        print('-----CHECKING TOKEN--------')
        #Checking the token 
        auth_url = 'https://ifzh62hr85.execute-api.us-east-2.amazonaws.com/prod/auth/user'

        data = {
            "token": token 
        }

        response = requests.post(auth_url, json=data)

        if response.status_code != 200:
            print('-----INVALID/EXPIRED TOKEN--------')
            return {
                'statusCode': 401,
                'body': 'Invalid Token'
            }
        
        userid = response.json()

        if "body" not in event:
            return {
                'statusCode': 400,
                'body': 'Request Body Required'
            }
        
        body = json.loads(event["body"])


        if "song" not in body or "artist" not in body:
            return {
                'statusCode': 400,
                'body': 'Song and artist is required'
            }
        
        song = body["song"]
        artist = body["artist"]

        spotify_token = get_token(client_id, client_secret, dbConn)
        print(f'TOKEN: {spotify_token}')

        uri = get_song_uri(spotify_token, song, artist)
        print(f'URI: {uri}')

        if uri is None: 
            return {
                'statusCode': 400,
                'body': 'song not found'
            }

        url = "https://api.spotify.com/v1/playlists/" + playlist_id + "/tracks"
        headers = post_auth_header(spotify_token)

        data = {
            "uris": [uri]
        }

        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            sql = "INSERT INTO playlist (userid, song, artist, songID) values (%s, %s, %s, %s)"
            params = [userid, song, artist, uri]
            datatier.perform_action(dbConn, sql, params)

            return {
                'statusCode': 200,
                'body': 'Successfully added the song'
            }

        else:
            return {
                'statusCode': 400,
                'body': 'Error adding song to playlist'
            }
    
    except Exception as err:
        print("**ERROR**")
        print(str(err))

        return {
            'statusCode': 400,
            'body': json.dumps(str(err))
        }





