from datetime import datetime, timedelta
from moviepy.editor import *
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime
import os
import socket
from pathlib import Path


def get_authenticated_service(creds_path):
    """Local oauth flow, returns authenticated youtube service object"""    
    CLIENT_SECRET_FILE = creds_path
    API_NAME = 'youtube'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    # Authenticate on each request for web version
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES)
    print('Select the google account where you would like to upload the video')
    credentials = flow.run_local_server()

    service = build(API_NAME, API_VERSION, credentials=credentials)
    return service


def upload_video(service, video):
    """Takes in authenticated yt service and custom video classm uploads video to youtube"""
    socket.setdefaulttimeout(100000)
    if not video.description:
        video.set_default_description()

    request_body = {
        'snippet': {
            'title': video.title,
            'categoryId': '20',
            'description': video.description,
            'tags': video.tags,
            'defaultLanguage': 'en'
        },
        'status': {
            'privacyStatus': video.privacyStatus,
            'selfDeclaredMadeForKids': False
        },
        'notifySubscribers': False
    }
    file = MediaFileUpload(video.filename)
    print(f'Uploading the following file: {video.filename}')


    print(f'Uploading video with the following information...\n{request_body}')
    print(file)
    response_upload = service.videos().insert(
        part = 'snippet,status',
        body = request_body,
        media_body = file
    ).execute()
    # Set thumbnail if valid file
    try:
        service.thumbnails().set(
            videoId=response_upload.get('id'),
            media_body=MediaFileUpload(video.thumbnail)
        ).execute()
    except FileNotFoundError:
        print(f'{video.thumbnail} could not be found, not updating thumbnail...')

    print('Upload complete!')