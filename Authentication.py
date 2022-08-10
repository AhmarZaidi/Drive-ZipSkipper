
# Generating Client_Secret file, pickle and Creating Service

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


def Create_Service(): # From (Channel: https://www.youtube.com/channel/UCvVZ19DRSLIC2-RUOeWx8ug)
    CLIENT_SECRET_FILE = 'client_secret.json' # Place this file (rename the file to 'client_secret.json') in same directory as this script. To get this file follow (https://www.youtube.com/watch?v=6bzzpda63H0). Credits (Channel: https://www.youtube.com/channel/UCvVZ19DRSLIC2-RUOeWx8ug)
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']

    cred = None

    pickle_file = f'token_{API_NAME}_{API_VERSION}.pickle'
    # print(pickle_file)

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_NAME, API_VERSION, credentials=cred)
        #print(API_SERVICE_NAME, 'service created successfully')
        return service
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None
