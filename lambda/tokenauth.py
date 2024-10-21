import os 
import json
import requests
import datetime 
import base64
import datatier
from configparser import ConfigParser

def lambda_handler(event, context): 
    try: 
        config_file = 'config.ini'
        os.environ['CREDENTIALS'] = config_file 

        configur = ConfigParser()
        configur.read(config_file)

        #Spotify 
        client_id = configur.get('spotify', 'client_id')
        client_secret = configur.get('spotify', 'client_secret')

        #RDS
        rds_endpoint = configur.get('rds', 'endpoint')
        rds_portnum = int(configur.get('rds', 'port_number'))
        rds_username = configur.get('rds', 'user_name')
        rds_pwd = configur.get('rds', 'user_pwd')
        rds_dbname = configur.get('rds', 'db_name')
        dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)


        try:
            code = event['queryStringParameters']['code']

            auth_string = client_id + ':' + client_secret
            auth_bytes = auth_string.encode("utf-8")
            auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

            headers = {
                "Authorization": "Basic " + auth_base64,
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": "https://localhost"
            }

            url = 'https://accounts.spotify.com/api/token'

            time = datetime.datetime.now(datetime.timezone.utc)
            response = requests.post(url, headers=headers, data=data)

            if response.status_code != 200:
                print('ACCESS TOKEN REQUEST WENT WRONG')
                return {
                    'statusCode': 400,
                    'body': 'ACCESS TOKEN REQUEST WENT WRONG'
                }
            
            body = response.json()
            access_token = body['access_token']
            refresh_token = body['refresh_token']
            expires_in = body['expires_in']


            sql = 'INSERT INTO spotifyToken (token, refresh, expiration_utc) values(%s, %s, %s)'
            params = [access_token, refresh_token, time + datetime.timedelta(seconds = expires_in)]
            datatier.perform_action(dbConn, sql, params)


            return {
                'statusCode': 200, 
                'body': 'success, close out from browser '
            }


        except Exception as err:
            print("**ERROR**")
            print("access denied ")

            return {
            'statusCode': 400,
            'body': "access denied"
        }


    except Exception as err: 
        print("**ERROR**")
        print(str(err))

        return {
            'statusCode': 400,
            'body': json.dumps(str(err))
        }
