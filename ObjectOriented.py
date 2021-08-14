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
class Video:
    def __init__(self, gameId, videoName, videoTitle, streamers, thumbnail, tags, description):
        self.gameId = gameId
        self.videoName = videoName
        self.videoTitle = videoTitle
        self.streamers = streamers
        self.thumbnail = thumbnail
        self.tags = tags
        self.desription = description
        
    def explain_self(self):
        print(self.gameId, self.videoName, self.streamers, self.thumbnail)

# Data structure for each individual clip
class Clip:
    def __init__(self, downloadLink, streamerName, filename):
        self.downloadLink = downloadLink
        self.streamerName = streamerName
        self.filename = filename

# General functions go below here
def get_credentials():
    with open('confidential.json', 'r') as fp:
        credentials = json.load(fp)
        return credentials




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
    # clipInfo = []
    # finalClipInfo = []
    # previousClips = []

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

        # # Keep going through results until 20 clips in spanish are acquired
        # if language[:2] == 'es':
        #     try:
        #         if data['pagination']['cursor']:
        #             cursor = data['pagination']['cursor']
        #         else:
        #             print('executing else block, and breaking')
        #             break
        #     except KeyError:
        #         print('Keyerror found, attempting to break out of loop')
        #         break

        #     for item in data['data']:
        #         # Add clip to list if language is Spanish AND broadcaster_name + clip title combination is unique
        #         if item['language'][:2] == 'es' and previousClips.count([item['broadcaster_name'], item['title']]) == 0 and 'vtube' not in item['broadcaster_name'].casefold():
        #             clipInfo.append([item['thumbnail_url'], item['broadcaster_name'], item['game_id']])
        #             previousClips.append([item['broadcaster_name'], item['title']])



        # Take the top 20 clips returned by clips api
        if language == None:
            for item in data['data']:
                cursor = data['pagination']['cursor']
                if len(clips) < numClips:
                    counter += 1
                    filename = item['game_id'] + item['broadcaster_name'] + str(counter) + '.mp4'
                    clipObj = Clip(item['thumbnail_url'], item['broadcaster_name'], filename)
                    clips.append(clipObj)
                    
        elif language[:2] == 'en':
            for item in data['data']:
                cursor = data['pagination']['cursor']
                if len(clips) < numClips and item['language'] == language[:2]:
                    counter += 1
                    filename = item['game_id'] + item['broadcaster_name'] + str(counter) + '.mp4'
                    clipObj = Clip(item['thumbnail_url'], item['broadcaster_name'], filename)
                    clips.append(clipObj)

                # clipInfo.append([item['thumbnail_url'], item['broadcaster_name'], item['game_id']])
                # previousClips.append([item['broadcaster_name'], item['title']])

        # cursor = data['pagination']['cursor']
    # Convert thumbnail_url to download link and create list with download link, broadcaster_name, game_id


    for clip in clips:
        clip.downloadLink = clip.downloadLink.split('-preview-')[0] + '.mp4'
        print(clip.downloadLink)

    print('Done getting clip info...')
    print(clips)

    # for link in clipInfo:
    #     finalClipInfo.append([link[0].split('-preview-')[0] + '.mp4', link[1], link[2]])
    # print('done getting clip info')
    # print(clipInfo)
    # print(len(clipInfo))
    # return finalClipInfo, game_id




















def main():
    credentials = get_credentials()
    get_clip_info(credentials, '29595')


if __name__ == "__main__":
    main()