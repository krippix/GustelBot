#Python native
import sys
import logging
import os
from pathlib import Path
import pickle

#Part of Project
import config

#External
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import requests
from googleapiclient.discovery import build

#API Daten aus Datei ziehen
def connectOAuth():
    
    credentials = None
    
    #token.pickle stores the user's credentails from previously successful logins
    if os.path.exists('{}{}{}'.format(config.youtubeFolder(), os.sep, "token.pickle")):
        logging.info("Loading YouTube Credentials from file...")
        with open('{}{}{}'.format(config.youtubeFolder(), os.sep, "token.pickle", 'rb')) as token:
                  credentials = pickle.load(token)
    
    #Check if credentials are valid, if not refresh token or ask for login
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            logging.info("Refreshing access token...")
            credentials.refresh(Request())
        else:
            logging.info("Fetching new tokens...")
            flow = InstalledAppFlow.from_client_secrets_file(
                Path('{}{}{}'.format(config.youtubeFolder(), os.sep, "client_secret.json")),
                scopes=['https://www.googleapis.com/auth/youtube','https://www.googleapis.com/auth/youtube.force-ssl']
            )
            #Erstellt einen lokalen Webserver um den Zugriff zuzulassen
            flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
            credentials = flow.credentials
            
            #Save the credentials
            with open('{}{}{}'.format(config.youtubeFolder(), os.sep, "token.pickle", 'wb')) as token2:
                logging.info("Saving YouTube credentials for later use...")
                pickle.dump(credentials, token2)
                
    
    return credentials
    

def createInstance():
     #Get Credentials
    try:
        credentials = connectOAuth()
    except Exception as e:
        logging.error("Failed to retrieve YouTube credentials "+str(e))
        return "Failed to authenticate to YouTube service."
    
    #Create YouTube instance
    youtube = build("youtube", "v3", credentials=credentials)
    
    return youtube

    
def createPlaylist(ctx):
    
    GustelBOT.ctx.send("Testnachricht")
    #ytInstance = createYouTubeInstance()
   
    

