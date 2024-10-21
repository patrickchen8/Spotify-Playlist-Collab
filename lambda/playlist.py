import os 
import datatier 
import requests 
import json
from configparser import ConfigParser

def lambda_handler(event, context):
    try: 
        config_file = 'config.ini'
        os.environ['CREDENTIALS'] = config_file 

        configur = ConfigParser()
        configur.read(config_file)

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


        sql = "SELECT song, artist, username FROM playlist INNER JOIN users ON playlist.userid = users.userid WHERE userid = %s"
        params = [userid]
        rows = datatier.retrieve_all_rows(dbConn, sql, params)

        return {
            'statusCode': 200,
            'body': json.dumps(rows)
        }


    except Exception as err:
        print("**ERROR**")
        print(str(err))

        return {
            'statusCode': 400,
            'body': json.dumps(str(err))
        }