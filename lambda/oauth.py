import os 
import json
from configparser import ConfigParser

#url = "https://accounts.spotify.com/authorize?client_id=33be6334cd8341b1b152d9dfdd190de3&response_type=code&redirect_uri=https://localhost&scope=playlist-modify-private+playlist-modify-public"


#Gets the authorization url needed 
def lambda_handler(event, context):
    try:
        print("STARTING: Spotify Authorization")

        #Configuration 
        config_file = 'config.ini'
        os.environ['CREDENTIALS'] = config_file 

        configur = ConfigParser()
        configur.read(config_file)
        client_id = configur.get('spotify', 'client_id')

        url = "https://accounts.spotify.com/authorize?client_id="
        response_type = "&response_type=code"
        redirect_uri = "&https://localhost"
        scope = "&scope=playlist-modify-private+playlist-modify-public"

        auth_url = url + client_id + response_type + redirect_uri + scope

        #Return the authorization url to the user 
        return {
            'statusCode': 200,
            'body': json.dumps(auth_url)
        }

    
    except Exception as err:
        print("**ERROR**")
        print(str(err))

        return {
            'statusCode': 400,
            'body': json.dumps(str(err))
        }