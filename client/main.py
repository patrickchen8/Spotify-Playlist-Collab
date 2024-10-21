import requests
import json

import uuid
import pathlib
import logging
import sys
import os
import base64
import webbrowser

from configparser import ConfigParser
from getpass import getpass


############################################################
#
# prompt
#
def prompt():
  """
  Prompts the user and returns the command number

  Parameters
  ----------
  None

  Returns
  -------
  Command number entered by user (0, 1, 2, ...)
  """
  print()
  print(">> Enter a command:")
  print("   0 => end")
  print("   1 => authorize")
  print("   2 => login")
  print("   3 => authenticate")
  print("   4 => signup")
  print("   5 => add song")
  print("   6 => remove song")
  print("   7 => entire playlist")
  print("   8 => songs I added")
  print("   9 => log out")

  cmd = input()

  if cmd == "":
    cmd = -1
  elif not cmd.isnumeric():
    cmd = -1
  else:
    cmd = int(cmd)

  return cmd


############################################################
#
# users
#
def spotifyAuth(baseurl):
  """
  Authorizes the application to the user's Spotify Account 

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/auth/url'
    url = baseurl + api

    res = requests.get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
        return
    
    body = res.json()
    webbrowser.open(body)
    return 

  except Exception as e:
    logging.error("users() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
#
# playlist
#
def playlist(baseurl, token):
  """
  Prints out all the songs in the playlist

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    #Checking if the token is not None 
    #
    if token is None:
      print("No current token, please login")
      return 
    
    #
    # call the web service:
    #
    api = '/playlist'
    url = baseurl + api
    req_header = {"Authentication": token}

    #
    # make request:
    #
    res = requests.get(url, headers=req_header)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400 or res.status_code == 401:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)

      return

    #
    # deserialize and extract jobs:
    #
    body = res.json()
    #
    # let's map each row into an Job object:
    #
    if len(body) == 0:
      print('No songs in the playlist')
      return 

    for row in body:
      print(f'{row[0]} by {row[1]} added by {row[2]}\n')
 
    return

  except Exception as e:
    logging.error("jobs() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

############################################################
#
# playlist
#
def playlistMe(baseurl, token):
  """
  Prints out all the songs in the playlist you added 

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    #Checking if the token is not None 
    #
    if token is None:
      print("No current token, please login")
      return 
    
    #
    # call the web service:
    #
    api = '/playlist/me'
    url = baseurl + api
    req_header = {"Authentication": token}

    #
    # make request:
    #
    res = requests.get(url, headers=req_header)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400 or res.status_code == 401:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)

      return

    #
    # deserialize and extract jobs:
    #
    body = res.json()
    
    
    if len(body) == 0:
      print('You have not added any songs to the playlist')


    for row in body:
      print(f'{row[0]} by {row[1]} added by {row[2]}\n')
 
    return

  except Exception as e:
    logging.error("jobs() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

############################################################
#
# login
#
def login(baseurl):
  """
  Prompts the user for a username and password, then tries
  to log them in. If successful, returns the token returned
  by the authentication service.

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  token if successful, None if not
  """

  try:
    username = input("username: ")
    password = getpass()
    duration = input("# of minutes before expiration? ")

    #
    # build message:
    #
    data = {"username": username, "password": password, "duration": duration}

    #
    # call the web service to upload the PDF:
    #
    api = '/auth/user'
    url = baseurl + api

    res = requests.post(url, json=data)

    #
    # clear password variable:
    #
    password = None

    #
    # let's look at what we got back:
    #
    if res.status_code == 401:
      #
      # authentication failed:
      #
      body = res.json()
      print(body)
      return None

    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # success, extract token:
    #
    body = res.json()

    token = body

    print("logged in, token:", token)
    return token

  except Exception as e:
    logging.error("login() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return None


############################################################
#
# authenticate
#
def authenticate(baseurl, token):
  """
  Since tokens expire, this function authenticates the 
  current token to see if still valid. Outputs the result.

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    if token is None:
      print("No current token, please login")
      return

    print("token:", token)

    #
    # build message:
    #
    data = {"token": token}

    #
    # call the web service to upload the PDF:
    #
    api = '/auth/user'
    url = baseurl + api

    res = requests.post(url, json=data)

    #
    # let's look at what we got back:
    #
    if res.status_code == 401:
      #
      # authentication failed:
      #
      body = res.json()
      print(body)
      return

    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # success, token is valid:
    #
    print("token is valid!")
    return

  except Exception as e:
    logging.error("authenticate() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  

############################################################
#
# SignUp
#
def signup(baseurl):
  """
  Created a new account and returns a token 

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  token if successful 
  """

  try:
    username = input("username: ")
    password = getpass()
    
    data = {"username": username, "password": password, "duration": 10}

    #
    #call the service to create a new account:
    #
    api = '/auth/new'
    url = baseurl + api

    res = requests.post(url, json=data)

    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      print('first')
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return
    

    api = '/auth/user'
    url = baseurl + api 

    res = requests.post(url, json=data)


    if res.status_code == 401:
      #
      # authentication failed:
      #
      body = res.json()
      print(body)
      return None

    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      print('second')
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # success, extract token:
    #
    body = res.json()

    token = body

    print("logged in, token:", token)
    return token

  

  except Exception as e:
    logging.error("signup() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
#
# addSong
#
def addSong(baseurl, token):
  """
  adds a song to the playlist 

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  None 
  """

  try:
    #
    #Checking if the token is not None 
    #
    if token is None:
      print("No current token, please login")
      return 
    

    song = input("Enter the name of song: ")
    artist = input("Enter the artist of the song: ")

    req_header = {"Authentication": token}
    
    data = {
      "song": song,
      "artist": artist 
    }

    #
    #call the service to create a new account:
    #
    api = '/song/add'
    url = baseurl + api


    res = requests.post(url, headers=req_header, json=data)
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400 or res.status_code == 401:
        # we'll have an error message
        body = res.text
        print("Error message:", body)
      #
      return
    
    print(f'Successfully Added {song} by {artist}')
    
    return 

  except Exception as e:
    logging.error("addSong() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  
############################################################
#
# removeSong
#
def removeSong(baseurl, token):
  """
  removes a song to the playlist 

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  None 
  """

  try:
    #
    #Checking if the token is not None 
    #
    if token is None:
      print("No current token, please login")
      return 
    

    song = input("Enter the name of song: ")
    artist = input("Enter the artist of the song: ")

    req_header = {"Authentication": token}
    
    data = {
      "song": song,
      "artist": artist 
    }

    #
    #call the service to create a new account:
    #
    api = '/song/remove'
    url = baseurl + api


    res = requests.delete(url, headers=req_header, json=data)
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400 or res.status_code == 401:
        # we'll have an error message
        body = res.text 
        print("Error message:", body)
      #
      return
    
    print(f'Successfully revmoed {song} by {artist}')
    
    return 

  except Exception as e:
    logging.error("addSong() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

############################################################
# main
#
try:
  print('** Welcome to BenfordApp with Authentication **')
  print()

  # eliminate traceback so we just get error message:
  sys.tracebacklimit = 0

  #
  # what config file should we use for this session?
  #
  config_file = 'client/client-config.ini'

  print("Config file to use for this session?")
  print("Press ENTER to use default, or")
  print("enter config file name>")
  s = input()

  if s == "":  # use default
    pass  # already set
  else:
    config_file = s

  #
  # does config file exist?
  #
  if not pathlib.Path(config_file).is_file():
    print("**ERROR: config file '", config_file, "' does not exist, exiting")
    sys.exit(0)

  #
  # setup base URL to web service:
  #
  configur = ConfigParser()
  configur.read(config_file)
  baseurl = configur.get('client', 'webservice')

  #
  # make sure baseurl does not end with /, if so remove:
  #
  if len(baseurl) < 16:
    print("**ERROR: baseurl '", baseurl, "' is not nearly long enough...")
    sys.exit(0)

  if baseurl == "https://YOUR_GATEWAY_API.amazonaws.com":
    print("**ERROR: update config file with your gateway endpoint")
    sys.exit(0)

  if baseurl.startswith("http:"):
    print("**ERROR: your URL starts with 'http', it should start with 'https'")
    sys.exit(0)

  lastchar = baseurl[len(baseurl) - 1]
  if lastchar == "/":
    baseurl = baseurl[:-1]

  #
  # initialize login token:
  #
  token = None

  #
  # main processing loop:
  #
  cmd = prompt()

  while cmd != 0:
    #
    if cmd == 1:
      spotifyAuth(baseurl)
    elif cmd == 2:
      token = login(baseurl)
    elif cmd == 3:
      authenticate(baseurl, token)
    elif cmd == 4:
      token = signup(baseurl)
    elif cmd == 5:
      addSong(baseurl, token)
    elif cmd == 6:
      removeSong(baseurl, token)
    elif cmd == 7:
      playlist(baseurl, token)
    elif cmd == 8:
      playlistMe(baseurl, token)
    elif cmd == 9:
      #
      # logout
      #
      token = None
    else:
      print("** Unknown command, try again...")
    #
    cmd = prompt()

  #
  # done
  #
  print()
  print('** done **')
  sys.exit(0)

except Exception as e:
  logging.error("**ERROR: main() failed:")
  logging.error(e)
  sys.exit(0)