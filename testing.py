from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

import pickle
import os
import socket

socket.setdefaulttimeout(100000)


CLIENT_SECRET_FILE = 'client_secret2.json'
API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = 'https://www.googleapis.com/auth/youtube.upload'

def get_authenticated_service():
    # Use pickle file if it exists
    if os.path.exists("CREDENTIALS_PICKLE_FILE"):
            with open("CREDENTIALS_PICKLE_FILE", 'rb') as f:
                credentials = pickle.load(f)

    # Otherwise authenticate user and create pickle file
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            scopes=SCOPES)
        credentials = flow.run_local_server()
        with open("CREDENTIALS_PICKLE_FILE", 'wb') as f:
                pickle.dump(credentials, f)

    service = build(API_NAME, API_VERSION, credentials=credentials)
    return service

def upload_video(service):
    request_body = {
        'snippet': {
            'title': 'Full Montage Upload',
            'categoryID': '20',
            'description': 'my desc',
            'tags': ['valorant', 'viking', 'gaming'],
            'defaultLanguage': 'en'
        },
        'status': {
            'privacyStatus': 'private',
            'selfDeclaredMadeForKids': False
        },
        'notifySubscribers': False
    }

    mediaFile = MediaFileUpload('Valorant.mp4')


    response_upload = service.videos().insert(
        part='snippet,status',
        body = request_body,
        media_body = mediaFile
    ).execute()
    service.thumbnails().set(
        videoId=response_upload.get('id'),
        media_body=MediaFileUpload('thumbnail1.jpg')
    ).execute()


def main():
    service = get_authenticated_service()
    upload_video(service)



if __name__ == "__main__":
    main()