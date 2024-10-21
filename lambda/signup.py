import os 
import datatier 
import json 
import auth

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

        username = " "
        password = " "

        if "body" not in event:
            return {
                'statusCode': 400,
                'body': "no body in the request"
         }
        
        body = json.loads(event["body"])
        
        if "username" in body and "password" in body:
            username = body["username"]
            password = body["password"]
        else: 
            return {
                'statusCode': 400,
                'body': 'missing credentials in body'
            }
        
        sql = "SELECT userid FROM users WHERE username = %s"
        params = [username]
        row = datatier.retrieve_one_row(dbConn, sql, params)

        if row == ():
            #Inserting credentials into the database 
            sql = "INSERT INTO users (username, pwdhash) values(%s, %s)"
            pwdhash = auth.hash_password(password)
            params = [username, pwdhash]
            datatier.perform_action(dbConn, sql, params)

            return {
                'statusCode': 200, 
                'body': 'sucessfully created the acount '
            }


        else:
            return {
                'statusCode': 400, 
                'body': 'username already taken'
            }


    except Exception as err:
        print("**ERROR**")
        print(str(err))

        return {
            'statusCode': 400,
            'body': json.dumps(str(err))
        }
