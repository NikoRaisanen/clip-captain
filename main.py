#!/bin/python
import requests, time, json, pprint, os
from datetime import datetime, timedelta
from moviepy.editor import *

# Site to download clips: https://clipr.xyz/ 

# Get url of 20 valorant clips

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
    counter = 0    
    for entry in clips:
        if entry[2] == '516575':
            filename = 'Valorant' + 'Clip' + str(counter) + '.mp4'
            counter += 1
        else:
            filename = 'Unknown' + 'Clip' + str(counter) + '.mp4'

        print(f'Downloading clip {counter} of {len(clips)}')
        r = requests.get(entry[0], allow_redirects=True)
        with open('./clips/' + filename, 'wb') as fp:
            fp.write(r.content)
# takes list of clips and combines them
def combine_clips(clips):
    videoObjects = []
    for clip in clips:
        video = VideoFileClip('clips/' + clip)
        video.resize(1920, 1080)
        videoObjects.append(video)

    final = concatenate_videoclips(videoObjects)
    final.write_videofile('final.mp4', fps=30)

def main():
    # BEGIN GETTING + DOWNLOADING CLIPS
    credentials = get_credentials()
    clips = get_clip_info(credentials)
    download_clips(clips)
    # END GETTING + DOWNLOADING CLIPS

    # BEGIN JOINING CLIPS TOGETHER
    combine_clips(os.listdir('clips'))

if __name__ == "__main__":
    main()