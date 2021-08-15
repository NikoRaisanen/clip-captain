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
    def __init__(self, gameName, filename, videoTitle, thumbnail, tags, description, streamers=[]):
        self.gameName = gameName
        self.filename = filename
        self.videoTitle = videoTitle
        self.streamers = streamers
        self.thumbnail = thumbnail
        self.tags = tags
        self.desription = description
    
    def __str__(self):
        return f'{self.gameName}\n{self.filename}\n{self.videoTitle}\n{self.thumbnail}\n{self.tags}\n{self.desription}\n{self.streamers}'

    def unique_streamers(self):
        self.streamers = list(set(self.streamers))
        
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


def download_clips(clips, videoStruct):
    counter = 0
    global downloadPath
    basePath = os.path.join(os.getcwd(), 'clips')
    downloadPath = os.path.join(basePath, Clip.gameName)
    if not os.path.exists(downloadPath):
        os.mkdir(downloadPath)

    # Create Video Object and define required attributes
    vidFileName = Clip.gameName + '.mp4'

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






def combine_clips(clips):
    videoObjects = []
    for clip in clips:
        # Add text below:
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





def get_authenticated_service():    
    CLIENT_SECRET_FILE = 'client_secret.json'
    API_NAME = 'youtube'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    # Authenticate on each request for web version
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES)
    credentials = flow.run_local_server()

    service = build(API_NAME, API_VERSION, credentials=credentials)
    return service




# def upload_video(service, videoStruct):
#     vidNumber = get_vid_number(game, language)
#     videoTitle = ''
#     email = ''
#     tags = []
#     # if thumbnail = None, do auto generation
#     # Format for autoTN is: gameName.lowercase() + "TN" + vidNumber + ".jpg" IF IT EXISTS
#     if game == 'Valorant':
#         if language == 'en':
#             videoTitle = f'Valorant Top Moments #{vidNumber} | Best Clips of the Week'
#             tags = ['valorant viking', 'valorant', 'viking', 'pro valorant', 'valorant clips', 'valorant moments', 'valorant compilation', 'valorant montage', 'valorant twitch', 'twitch']
#             email = 'valorantvikingclips@gmail.com'
#         elif language == 'es':
#             videoTitle = f'Valorant Top Moments #{vidNumber} | Best Clips of the Week'
#             tags = ['valorant viking', 'valorant', 'viking', 'pro valorant', 'valorant clips', 'valorant moments', 'valorant compilation', 'valorant montage', 'valorant twitch', 'twitch']
#             email = 'valorantvikingclips@gmail.com'
#     # WHEN EXPANDING TO GTAV COME UP WITH TITLE + VID NUMBER
#     # CHANGE CONTENT IN SPANISH ELIF
#     elif game == 'GTAV':
#         if language == 'en':
#             videoTitle = f'GTA V Clips of the Week #{vidNumber} | GTA 5 RP Highlights'
#             tags = ['Twitch', 'gta 5', 'gta rp', 'roleplay', 'gta roleplay', 'twitch gta', 'gta v', 'gta highlights']
#             email = 'valorantvikingclips@gmail.com'
#         elif language == 'es':
#             videoTitle = 'First GTAV Video'
#             tags = ['first GTAV tags']

#     elif game == 'Just Chatting':
#         if language == 'en':
#             videoTitle = f'Most Popular JUST CHATTING Clips of the Week #{vidNumber}'
#             tags = ['twitch', 'justchatting', 'just chatting', 'twitch 2021', 'twitch july', 'twitch streamers', 'twitch funny', 'best of twitch']
#             email = 'theholyfishmoley@gmail.com'
#         elif language == 'es':
#             videoTitle = f'Los Mejores Clips de Twitch Español Just Chatting #{vidNumber}'
#             tags = ['twitch', 'twitch español', 'twitch mexico', 'twitch chicas', 'twitch españa', 'twitch en español', 'just chatting', 'asmr']
#             email = 'carnedeoveja737@gmail.com'

#     elif game == 'ASMR':
#         if language == 'en':
#             videoTitle = f'🍑💦 Best of Twitch ASMR Week #{vidNumber}'
#             tags = ['twitch', 'asmr', 'twitch asmr', 'asmr of the week', 'ear licking asmr', 'twitch girl', 'asmr compilation', 'twitch wardrobe malfunction']
#             email = 'theholyfishmoley@gmail.com'
#         elif language == 'es':
#             videoTitle = f'🍑💦 ASMR en Español | Los Mejores Videos de ASMR Twitch #{vidNumber}'
#             tags = ['twitch', 'twitch español', 'twitch mexico', 'twitch chicas', 'twitch españa', 'twitch en español', 'just chatting', 'asmr']
#             email = 'carnedeoveja737@gmail.com'

#     elif game == 'PHB':
#         if language == 'en':
#             videoTitle = f'Twitch Hot Tub Meta | Fails and Wins #{vidNumber} 🍑💦'
#             tags = ['twitch', 'justchatting', 'hot tub', 'pool', 'swimsuit twitch', 'twitch beach', 'twitch girl', 'twitch thot', 'twitch pool', 'amouranth']
#             email = 'theholyfishmoley@gmail.com'
#         elif language == 'es':
#             videoTitle = f'🍑💦 Mujeres de Twitch Español | Hot Tubs Piscinas y Playas #{vidNumber}'
#             tags = ['twitch', 'twitch español', 'twitch mexico', 'twitch chicas', 'twitch españa', 'twitch en español', 'playa', 'piscina']
#             email = 'carnedeoveja737@gmail.com'

#     elif game == 'Dota':
#             videoTitle = f'Top Dota 2 CLips of the Week {vidNumber} | Twitch Highlights'
#             tags = ['first GTAV tags']
#     else:
#         videoTitle = 'PLACEHOLDER VIDEO TITLE' 
#         tags = ['placeholder tags']
#         email = 'the contact information found on our about page'

#     streamers = list(set(streamers))
#     streamerCredit = ''
#     for streamer in streamers:
#         streamer = "https://www.twitch.tv/" + streamer
#         streamerCredit = streamerCredit + "\n" + streamer

#     # If no thumbnail, use auto-generated thumbnail. Else, use provided thumbnail
#     if not thumbnail:
#         filename = f'{game.casefold()}TN{language}{vidNumber}.jpg'
#         thumbnail = os.path.join(os.getcwd(), 'assets', filename)
#         print(f'Using {thumbnail} as thumbnail for this video!')
#     else:
#         pass

#     if language == 'en':
#         description = f'{videoTitle}\n\nMake sure to support the streamers in the video!\n{streamerCredit}\n\nEverything licensed under Creative Commons: By Attribution 3.0:\n» https://creativecommons.org/licenses/by/3.0/\n\n📧If you would like to stop having your clips featured on this channel just send us an email at {email}'
#     elif language == 'es':
#         description = f'{videoTitle}\n\nApoya a los streamers en el video!\n{streamerCredit}\n\n» https://creativecommons.org/licenses/by/3.0/\n📧📧Si no quieres aparecer en estos videos, envianos mensaje a {email}'

#     # description = f'{videoTitle}\n\nMake sure to support the streamers in the video!\n{streamerCredit}\n\nEverything licensed under Creative Commons: By Attribution 3.0:\n» https://creativecommons.org/licenses/by/3.0/\n\n📧If you would like to stop having your clips featured on this channel just send us an email at {email}'
#     request_body = {
#         'snippet': {
#             'title': videoTitle,
#             'categoryId': '20',
#             'description': description,
#             'tags': tags,
#             'defaultLanguage': 'en'
#         },
#         'status': {
#             'privacyStatus': 'public',
#             'selfDeclaredMadeForKids': False
#         },
#         'notifySubscribers': False
#     }
#     mediaFile = MediaFileUpload(videoName)
#     print(f'Uploading the following file: {videoName}')


#     print(f'Uploading video with the following information...\n{request_body}')
#     print(mediaFile)
#     response_upload = service.videos().insert(
#         part = 'snippet,status',
#         body = request_body,
#         media_body = mediaFile
#     ).execute()
#     service.thumbnails().set(
#         videoId=response_upload.get('id'),
#         media_body=MediaFileUpload(thumbnail)
#     ).execute()

#     print('Upload complete!')
#     # END UPLOAD TO YOUTUBE








def main():
    beginTime = datetime.now()
    # Increase socket default timemout due to connection dropping during large file uploads
    socket.setdefaulttimeout(100000)

    # GET THE BELOW INFORMATION FROM USER ON WEBPAGE
    gameName = 'VALORANT'
    Clip.gameName = gameName
    filename = Clip.gameName + '.mp4'
    videoTitle = 'My Video #1'
    thumbnail = '[link to thumbnail]'
    tags = ['valorant', 'top', 'plays']
    description = 'This is my description'

    # Creating Video Object
    videoStruct = VideoObj(gameName, filename, videoTitle, thumbnail, tags, description)
    credentials = get_credentials()
    # See if possible to create dropdown menu for games
    gameId = get_game_id(gameName, credentials)
    clips = get_clip_info(credentials, gameId, numClips=20)
    download_clips(clips, videoStruct)
    vidPath = combine_clips(clips)
    videoStruct.filename = vidPath
    ytService = get_authenticated_service()
    # upload_video(ytService, videoStruct)
    

    endTime = datetime.now()
    print(f'The execution of this script took {(endTime - beginTime).seconds} seconds')

if __name__ == "__main__":
    main()