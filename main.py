#!/bin/python
import requests, json, os
from datetime import datetime, timedelta
from moviepy.editor import *
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

import pickle
import os
import socket


# Get url of 20 valorant clips
# BEGIN CLIP PROCUREMENT, DOWNLOAD, AND COMBINING

def get_credentials():
    with open('confidential.json', 'r') as fp:
        credentials = json.load(fp)
        return credentials

def get_clip_info(credentials):
    # Get current time in RFC3339 format with T and Z
    timeNow = datetime.now().isoformat()
    timeNow = timeNow.split('.')[0]
    timeNow = timeNow + "Z"
    timeNow = datetime.strptime(timeNow, '%Y-%m-%dT%H:%M:%SZ')

    # Subtract current time by 7 days to get startDate (lower bounds of date to look for clips)
    startDate = timeNow - timedelta(days=7)
    startDate = startDate.isoformat()
    startDate = startDate + "Z"
    # Example of startDate variable:
    # 2021-06-28T10:53:47Z
    # Use startData var for started_at query parameter for twitch clip api calls

    # Call twitch api to get thumbnail url, broadcaster name, game id
    clipInfo = []
    finalClipInfo = []
    clipsAPI = 'https://api.twitch.tv/helix/clips'
    PARAMS = {'game_id': 516575, 'started_at': startDate}
    HEADERS = {'Client-Id': credentials['twitch_client_id'], 'Authorization': 'Bearer ' + credentials['access_bearer_token']}
    r = requests.get(url=clipsAPI, params=PARAMS, headers=HEADERS)
    data = r.json()

    for entry in data['data']:
        clipInfo.append([entry['thumbnail_url'], entry['broadcaster_name'], entry['game_id']])

    # Convert thumbnail_url to download link and create list with download link, broadcaster_name, game_id
    for link in clipInfo:
        finalClipInfo.append([link[0].split('-preview-')[0] + '.mp4', link[1], link[2]])

    return finalClipInfo

def download_clips(clips):
    # Downloads clips within the below for loop
    # [0] is download url
    # [1] is streamer name
    # [2] is game id
    # fullInfo list contains: download url, streamer name, game id, 
    fullInfo = []
    streamers = []
    counter = 0
    game = ''    
    for entry in clips:
        if entry[2] == '516575':
            filename = 'Valorant' + entry[1] + 'Clip' + str(counter) + '.mp4'
            counter += 1
            game = 'Valorant'
        else:
            filename = 'Unknown' + entry[1] + 'Clip' + str(counter) + '.mp4'
            game = 'Unknown'

        print(f'Downloading clip {counter} of {len(clips)}')
        r = requests.get(entry[0], allow_redirects=True)
        with open('./clips/' + filename, 'wb') as fp:
            fp.write(r.content)

        streamers.append(entry[1])
        # Return list of streamer names (give credit in youtube description)
        # Set conversion used to remove duplicates
    return game

# takes list of clips and combines them
def combine_clips(clips, game):
    videoObjects = []
    for clip in clips:
        # Add text below:
        streamerName = clip.split(game)[1].split('Clip')[0]
        
        video = VideoFileClip('clips/' + clip, target_resolution=(1080,1920))
        txt_clip = TextClip(streamerName, fontsize = 60, color = 'white',stroke_color='black',stroke_width=2, font="Fredoka-One")
        txt_clip = txt_clip.set_pos((0.8, 0.9), relative=True).set_duration(video.duration)
        video = CompositeVideoClip([video, txt_clip]).set_duration(video.duration)
        videoObjects.append(video)

    # Make transition clip 1 second long and halve the volume
    transition = VideoFileClip('tvstatictransition.mp4').fx(afx.volumex, 0.5)
    transition = transition.subclip(0, -1)
    # video name based on game
    videoName = game + '.mp4'
    final = concatenate_videoclips(videoObjects, transition=transition, method='compose')
    # final = concatenate_videoclips(videoObjects, transition=transition, method='compose')
    final.write_videofile(videoName, fps=60, bitrate="6000k")

    # END CLIP PROCUREMENT, DOWNLOAD, AND COMBINING
    # BEGIN UPLOAD TO YOUTUBE
def get_authenticated_service():    
    CLIENT_SECRET_FILE = 'client_secret2.json'
    API_NAME = 'youtube'
    API_VERSION = 'v3'
    SCOPES = 'https://www.googleapis.com/auth/youtube.upload'

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
    # Increase socket default timemout due to connection dropping during large file uploads


    print(f'Uploading video with the following information...\n{request_body}')
    response_upload = service.videos().insert(
        part = 'snippet,status',
        body = request_body,
        media_body = mediaFile
    ).execute()
    service.thumbnails().set(
        videoId=response_upload.get('id'),
        media_body=MediaFileUpload('thumbnail1.jpg')
    ).execute()

    # END UPLOAD TO YOUTUBE

def main():
    socket.setdefaulttimeout(100000)
    # # BEGIN GETTING + DOWNLOADING CLIPS
    # credentials = get_credentials()
    # clips = get_clip_info(credentials)
    # # ^ From here and above there is download link, streamer name, game id 
    # game = download_clips(clips)
    # print(f'This video is about: {game}')
    # # END GETTING + DOWNLOADING CLIPS

    # # Join clips together, writes an mp4 file in the cwd
    # allClips = os.listdir('clips')
    # combine_clips(allClips, game)
    youtube = get_authenticated_service()
    upload_video(youtube)


if __name__ == "__main__":
    main()