#!/bin/python
import requests, json, os
from datetime import datetime, timedelta
from moviepy.editor import *
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime

from google.auth.transport.requests import Request
import pickle
import os
import socket

# Data structure for the final video, used to populate information in Youtube Upload API
class VideoObj:
    def __init__(self, gameName, filename, videoTitle, thumbnail, tags, description, privacyStatus, streamers=[]):
        self.gameName = gameName
        self.filename = filename
        self.videoTitle = videoTitle
        self.streamers = streamers
        self.thumbnail = thumbnail
        self.tags = tags
        self.description = description
        self.privacyStatus = privacyStatus
    
    def __str__(self):
        return f'{self.gameName}\n{self.filename}\n{self.videoTitle}\n{self.thumbnail}\n{self.tags}\n{self.desription}\n{self.streamers}'

    def unique_streamers(self):
        self.streamers = list(set(self.streamers))
    
    def set_default_description(self):
        streamerCredit = ''
        for streamer in self.streamers:
            streamer = "https://www.twitch.tv/" + streamer
            streamerCredit = streamerCredit + "\n" + streamer

        self.description = f'{self.videoTitle}\n\nMake sure to support the streamers in the video!\n{streamerCredit}'
            

# Data structure for each individual clip
class Clip:
    gameName = ''
    def __init__(self, downloadLink, streamerName, filename):
        self.downloadLink = downloadLink
        self.streamerName = streamerName
        self.filename = filename

# General functions go below here
def get_credentials():
    with open('confidential.json', 'r') as fp:
        credentials = json.load(fp)
        return credentials

# Possibly use dropdown on front-end to get the gameName
def get_game_id(gameName, credentials):
    gamesAPI = 'https://api.twitch.tv/helix/games'
    PARAMS = {'name': gameName}
    HEADERS = {'Client-Id': credentials['twitch_client_id'], 'Authorization': 'Bearer ' + credentials['access_bearer_token']}
    r = requests.get(url=gamesAPI, params=PARAMS, headers=HEADERS)
    data = r.json()

    if data['data'] == []:
        # SHOW THIS TO USER WHEN THEY TRY TO SUBMIT
        raise Exception(f'*****COULD NOT RESOLVE GAMEID FOR {gameName}*****')
    else:
        gameId = data['data'][0]['id']
        Clip.gameName = gameName

    return gameId

# game_id, pastDays, numClips, language <-- all vars declared on program start
def get_clip_info(credentials, game_id, pastDays=7, numClips = 20, first = 50, cursor = None, language =None):
    print(f'Language to be used is: {language}')
    # Get current time in RFC3339 format with T and Z
    timeNow = datetime.now().isoformat()
    timeNow = timeNow.split('.')[0]
    timeNow = timeNow + "Z"
    timeNow = datetime.strptime(timeNow, '%Y-%m-%dT%H:%M:%SZ')

    # Subtract current time by 7 days to get startDate (lower bounds of date to look for clips)
    startDate = timeNow - timedelta(pastDays)
    startDate = startDate.isoformat()
    startDate = startDate + "Z"
    # Example of startDate variable:
    # 2021-06-28T10:53:47Z
    # Use startData var for started_at query parameter for twitch clip api calls

    # Call twitch api to get thumbnail url, broadcaster name, game id
    counter = 1
    clips = []


    # Keep paginating through twitch clips API until 20 valid clips
    while len(clips) < numClips:
        print(f'Query #{counter} for valid clips')
        clipsAPI = 'https://api.twitch.tv/helix/clips'
        PARAMS = {'game_id': game_id, 'started_at': startDate, 'first': first, 'after': cursor}
        HEADERS = {'Client-Id': credentials['twitch_client_id'], 'Authorization': 'Bearer ' + credentials['access_bearer_token']}
        r = requests.get(url=clipsAPI, params=PARAMS, headers=HEADERS)
        data = r.json()


        # Take the top 20 clips returned by clips api
        if language == None:
            for item in data['data']:
                cursor = data['pagination']['cursor']
                if len(clips) < numClips:
                    counter += 1
                    filename = Clip.gameName + item['broadcaster_name'] + str(counter) + '.mp4'
                    downloadLink = item['thumbnail_url'].split('-preview-')[0] + '.mp4'
                    clipObj = Clip(downloadLink, item['broadcaster_name'], filename)
                    clips.append(clipObj)

        elif language[:2] == 'en':
            for item in data['data']:
                cursor = data['pagination']['cursor']
                if len(clips) < numClips and item['language'] == language[:2]:
                    counter += 1
                    filename = Clip.gameName + item['broadcaster_name'] + str(counter) + '.mp4'
                    downloadLink = item['thumbnail_url'].split('-preview-')[0] + '.mp4'
                    clipObj = Clip(downloadLink, item['broadcaster_name'], filename)
                    clips.append(clipObj)

    print('Done getting clip info...')
    return clips


def download_clips(clips, videoStruct):
    counter = 0
    global downloadPath
    basePath = os.path.join(os.getcwd(), 'clips')
    downloadPath = os.path.join(basePath, Clip.gameName)
    if not os.path.exists(downloadPath):
        os.mkdir(downloadPath)

    for clip in clips:
        r = requests.get(clip.downloadLink, allow_redirects=True)
        videoStruct.streamers.append(clip.streamerName)
        with open(os.path.join(downloadPath, clip.filename), 'wb') as fp:
            try:
                fp.write(r.content)
                print(f'Downloading clip {str(counter + 1)} of {len(clips)} to {os.path.join(downloadPath, clip.filename)}')
            except:
                print("except block executed")

        counter += 1
    videoStruct.unique_streamers()
    print(f'Here are the unique streamers:\n{videoStruct.streamers}')
    print(f'Finished downloading {counter} clips for {Clip.gameName}!')






def combine_clips(clips, transition):
    videoObjects = []
    for clip in clips:
        # Add text below:
        video = VideoFileClip(os.path.join(downloadPath, clip.filename), target_resolution=(1080,1920))
        txt_clip = TextClip(clip.streamerName, fontsize = 60, color = 'white',stroke_color='black',stroke_width=2, font="Fredoka-One")
        txt_clip = txt_clip.set_pos((0.8, 0.9), relative=True).set_duration(video.duration)
        video = CompositeVideoClip([video, txt_clip]).set_duration(video.duration)
        videoObjects.append(video)

    if transition == '':
        transition = 'assets/tvstatictransition.mp4'
    else:
        pass
    print(f'Using {transition} as the transitioning media')
    print('done creating list of video objects')
    # Make transition clip 1 second long and halve the volume
    transition = VideoFileClip(transition).fx(afx.volumex, 0.5)
    transition = transition.subclip(0, -1)
    # video name based on game
    videoName = Clip.gameName + '.mp4'
    print('Beginning to concatenate video clips...')
    final = concatenate_videoclips(videoObjects, transition=transition, method='compose')
    # final = concatenate_videoclips(videoObjects, transition=transition, method='compose')
    final.write_videofile(os.path.join(os.getcwd(), 'finalVideos', videoName), fps=60, bitrate="6000k")
    return os.path.join(os.getcwd(), 'finalVideos', videoName)

    # END CLIP PROCUREMENT, DOWNLOAD, AND COMBINING





def get_authenticated_service():    
    CLIENT_SECRET_FILE = 'client_secret.json'
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




def upload_video(service, videoStruct):
    socket.setdefaulttimeout(100000)
    if videoStruct.description != '':
        pass    # no additional handling needed
    else:
        videoStruct.set_default_description()


    request_body = {
        'snippet': {
            'title': videoStruct.videoTitle,
            'categoryId': '20',
            'description': videoStruct.description,
            'tags': videoStruct.tags,
            'defaultLanguage': 'en'
        },
        'status': {
            'privacyStatus': videoStruct.privacyStatus,
            'selfDeclaredMadeForKids': False
        },
        'notifySubscribers': False
    }
    mediaFile = MediaFileUpload(videoStruct.filename)
    print(f'Uploading the following file: {videoStruct.filename}')


    print(f'Uploading video with the following information...\n{request_body}')
    print(mediaFile)
    response_upload = service.videos().insert(
        part = 'snippet,status',
        body = request_body,
        media_body = mediaFile
    ).execute()
    # Set thumbnail if valid file
    try:
        service.thumbnails().set(
            videoId=response_upload.get('id'),
            media_body=MediaFileUpload(videoStruct.thumbnail)
        ).execute()
    except FileNotFoundError:
        print(f'{videoStruct.thumbnail} could not be found, using auto-generated thumbnail!')

    print('Upload complete!')
    # END UPLOAD TO YOUTUBE

def all_in_one():
    beginTime = datetime.now()
    # Increase socket default timemout due to connection dropping during large file uploads
    socket.setdefaulttimeout(100000)

    # GET THE BELOW INFORMATION FROM USER ON WEBPAGE
    gameName = 'Hearthstone'
    Clip.gameName = gameName
    filename = Clip.gameName + '.mp4'
    videoTitle = 'My Video #1'
    thumbnail = '[link to thumbnail]' # optional
    tags = ['valorant', 'top', 'plays']
    description = '' #optional
    privacyStatus = 'private'
    transition = 'assets/tvstatictransition.mp4'

    # Creating Video Object
    videoStruct = VideoObj(gameName, filename, videoTitle, thumbnail, tags, description, privacyStatus)
    credentials = get_credentials()
    ytService = get_authenticated_service()
    # See if possible to create dropdown menu for games
    gameId = get_game_id(gameName, credentials)
    clips = get_clip_info(credentials, gameId, numClips=2)
    download_clips(clips, videoStruct)
    vidPath = combine_clips(clips, transition)
    videoStruct.filename = vidPath
    # ytService = get_authenticated_service()
    upload_video(ytService, videoStruct)
    

    endTime = datetime.now()
    print(f'The execution of this script took {(endTime - beginTime).seconds} seconds')

def status_update(message):
    return message

def main():
    beginTime = datetime.now()
    # Increase socket default timemout due to connection dropping during large file uploads
    socket.setdefaulttimeout(100000)

    # GET THE BELOW INFORMATION FROM USER ON WEBPAGE
    gameName = 'Hearthstone'
    Clip.gameName = gameName
    filename = Clip.gameName + '.mp4'
    videoTitle = 'My Video #1'
    thumbnail = '[link to thumbnail]' # optional
    tags = ['valorant', 'top', 'plays']
    description = '' #optional
    privacyStatus = 'private'
    transition = 'assets/tvstatictransition.mp4'

    # Creating Video Object
    videoStruct = VideoObj(gameName, filename, videoTitle, thumbnail, tags, description, privacyStatus)
    credentials = get_credentials()
    # See if possible to create dropdown menu for games
    gameId = get_game_id(gameName, credentials)
    clips = get_clip_info(credentials, gameId, numClips=2)
    download_clips(clips, videoStruct)
    vidPath = combine_clips(clips, transition)
    videoStruct.filename = vidPath
    ytService = get_authenticated_service()
    upload_video(ytService, videoStruct)
    

    endTime = datetime.now()
    print(f'The execution of this script took {(endTime - beginTime).seconds} seconds')

if __name__ == "__main__":
    main()