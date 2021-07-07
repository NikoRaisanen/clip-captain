from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

import time
import pickle
import os

CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = 'https://www.googleapis.com/auth/youtube.upload'

if os.path.exists("CREDENTIALS_PICKLE_FILE"):
        with open("CREDENTIALS_PICKLE_FILE", 'rb') as f:
            credentials = pickle.load(f)
else:
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES)
    credentials = flow.run_local_server()
    with open("CREDENTIALS_PICKLE_FILE", 'wb') as f:
            pickle.dump(credentials, f)

# credentials = flow.run_console()

print('before building service')
service = build(API_NAME, API_VERSION, credentials=credentials)
print('after building service')
request_body = {
    'snippet': {
        'title': 'test from pickle file',
        'categoryID': 1,
        'description': 'my desc'
    },
    'status': {
        'privacyStatus': 'private',
        'selfDeclaredMadeForKids': False
    },
    'notifySubscribers': False
}

mediaFile = MediaFileUpload('tvstatictransition.mp4')


response_upload = service.videos().insert(
    part='snippet,status',
    body = request_body,
    media_body = mediaFile
).execute()
service.thumbnails().set(
    videoId=response_upload.get('id'),
    media_body=MediaFileUpload('thumbnail1.jpg')
).execute()

print(service)
print("end of script")



