import requests 
import json 
import base64
import datatier
import datetime 

#Gets the necessary token to access Spotify  
def get_token(client_id, client_secret, dbConn): 
    sql = "SELECT token, refresh, expiration_utc FROM spotifyToken"
    row = datatier.retrieve_one_row(dbConn, sql)

    if row == ():
        print("Access Token Does Not Exist")
        print("Authorization Needed")
        return None 

    token, refresh, expiration = row
    #Refresh needed 
    if datetime.datetime.now(datetime.timezone.utc) >= expiration.replace(tzinfo= datetime.timezone.utc):
        return refreshToken(token, refresh, dbConn, client_id, client_secret)
    
    else:
        return token 


#Refreshes the token if expired and returns a new token 
def refreshToken(token, refresh, dbConn, client_id, client_secret):
    url = 'https://accounts.spotify.com/api/token'

    auth_string = client_id + ':' + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh,
        'client_id': client_id
    }

    time = datetime.datetime.now(datetime.timezone.utc)

    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        print(response.json())
        return None 
    
    body = response.json()

    t = body['access_token']
    #r = body['refresh_token']
    expires_in = body['expires_in']

    sql = "UPDATE spotifyToken SET token = %s, expiration_utc = %s WHERE token = %s"
    params = [t, time + datetime.timedelta(seconds=expires_in), token]

    datatier.perform_action(dbConn, sql, params)

    return t 
   

   
#Returns the required Authorization header with token for GET Request 
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

#Returns the required Authorization header with token for POST Request 
def post_auth_header(token):
    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type": "application/json"
    }

    return headers 

#Searches for the track and return the uri of the first track 
def get_song_uri(token, song_name, artist): 
    url = "https://api.spotify.com/v1/search?"
    song_name = song_name.replace(" ", "+")
    artist = artist.replace(" ", "+")

    q = "q=" + song_name + "+" + artist
    type = "&type=track"
    limit = "&limit=10"

    url = url + q + type + limit
    print(url)

    headers = get_auth_header(token)

    response = requests.get(url, headers=headers)
    print(response.status_code)

    if response.status_code != 200: 
        print("ERORR: ")
        return None 
    
    body = response.json()
    tracks = body['tracks']

    if tracks['total'] == 0:
        print('Song does not exist')
        return None 

    track = tracks['items'][0]

    uri = track['uri']

    return uri 