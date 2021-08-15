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
    def __init__(self, gameName, filename, streamers=[], videoTitle='', thumbnail=None, tags=[], description=''):
        self.gameId = gameName
        self.filename = filename
        self.videoTitle = videoTitle
        self.streamers = streamers
        self.thumbnail = thumbnail
        self.tags = tags
        self.desription = description
        
    def explain_self(self):
        print(self.gameId, self.videoName, self.streamers, self.thumbnail)

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
    print(f'Language to be used is {language}')
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
    counter = 0
    clips = []


    # Keep paginating through twitch clips API until 20 valid clips
    while len(clips) < numClips:
        print(f'Iteration #{counter}')
        print(clips)
        print(len(clips))
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


def download_clips(clips):
    counter = 0
    global downloadPath
    basePath = os.path.join(os.getcwd(), 'clips')
    downloadPath = os.path.join(basePath, Clip.gameName)
    if not os.path.exists(downloadPath):
        os.mkdir(downloadPath)

    # Create Video Object and define required attributes
    vidFileName = Clip.gameName + '.mp4'
    Video = VideoObj(Clip.gameName, vidFileName, [])

    for clip in clips:
        r = requests.get(clip.downloadLink, allow_redirects=True)
        Video.streamers.append(clip.streamerName)
        with open(os.path.join(downloadPath, clip.filename), 'wb') as fp:
            try:
                fp.write(r.content)
                print(f'Downloading clip {str(counter + 1)} of {len(clips)} to {os.path.join(downloadPath, clip.filename)}')
            except:
                print("except block executed")

        counter += 1
    print(f'Finished downloading {counter} clips for {Clip.gameName}!')
    return Video






def combine_clips(clips):
    videoObjects = []
    for clip in clips:
        # Add text below:
        streamerName = clip.streamerName
        
        video = VideoFileClip(os.path.join(downloadPath, clip.filename), target_resolution=(1080,1920))
        txt_clip = TextClip(clip.streamerName, fontsize = 60, color = 'white',stroke_color='black',stroke_width=2, font="Fredoka-One")
        txt_clip = txt_clip.set_pos((0.8, 0.9), relative=True).set_duration(video.duration)
        video = CompositeVideoClip([video, txt_clip]).set_duration(video.duration)
        videoObjects.append(video)

    print('done creating list of video objects')
    # Make transition clip 1 second long and halve the volume
    transition = VideoFileClip('assets/tvstatictransition.mp4').fx(afx.volumex, 0.5)
    transition = transition.subclip(0, -1)
    # video name based on game
    videoName = Clip.gameName + '.mp4'
    print('Beginning to concatenate video clips...')
    final = concatenate_videoclips(videoObjects, transition=transition, method='compose')
    # final = concatenate_videoclips(videoObjects, transition=transition, method='compose')
    final.write_videofile(os.path.join(os.getcwd(), 'finalVideos', videoName), fps=60, bitrate="6000k")
    return os.path.join(os.getcwd(), 'finalVideos', videoName)

    # END CLIP PROCUREMENT, DOWNLOAD, AND COMBINING















def main():
    beginTime = datetime.now()
    # Increase socket default timemout due to connection dropping during large file uploads
    socket.setdefaulttimeout(100000)

    credentials = get_credentials()
    # See if possible to create dropdown menu for games
    gameName = 'VALORANT'
    gameId = get_game_id(gameName, credentials)
    clips = get_clip_info(credentials, gameId, numClips=3)
    videoObj = download_clips(clips)
    vidPath = combine_clips(clips)
    print(vidPath)

    endTime = datetime.now()
    print(f'The execution of this script took {(endTime - beginTime).seconds} seconds')

if __name__ == "__main__":
    main()