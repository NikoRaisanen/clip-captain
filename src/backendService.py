#!/bin/python
import requests, json, os
from datetime import datetime, timedelta
from moviepy.editor import *
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime
import os
import socket
import helpers.auth as auth
import helpers.twitch as twitch 


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
    # Create finalVideos folder if it doesn't exist
    if not os.path.exists(os.path.join(os.getcwd(), 'finalVideos')):
        os.mkdir('finalVideos')
    final.write_videofile(os.path.join(os.getcwd(), 'finalVideos', videoName), fps=60, bitrate="6000k", threads=2)
    return os.path.join(os.getcwd(), 'finalVideos', videoName)


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

# def all_in_one():
#     beginTime = datetime.now()
#     # Increase socket default timemout due to connection dropping during large file uploads
#     socket.setdefaulttimeout(100000)

#     # GET THE BELOW INFORMATION FROM USER ON WEBPAGE
#     gameName = 'Hearthstone'
#     Clip.gameName = gameName
#     filename = Clip.gameName + '.mp4'
#     videoTitle = 'My Video #1'
#     thumbnail = '[link to thumbnail]' # optional
#     tags = ['valorant', 'top', 'plays']
#     description = '' #optional
#     privacyStatus = 'private'
#     transition = 'assets/tvstatictransition.mp4'

#     # Creating Video Object
#     videoStruct = VideoObj(gameName, filename, videoTitle, thumbnail, tags, description, privacyStatus)
#     credentials = get_credentials()
#     ytService = get_authenticated_service()
#     # See if possible to create dropdown menu for games
#     gameId = get_game_id(gameName, credentials)
#     clips = get_clip_info(credentials, gameId, numClips=2)
#     download_clips(clips, videoStruct)
#     vidPath = combine_clips(clips, transition)
#     videoStruct.filename = vidPath
#     # ytService = get_authenticated_service()
#     upload_video(ytService, videoStruct)
    
#     endTime = datetime.now()
#     print(f'The execution of this script took {(endTime - beginTime).seconds} seconds')


def main():
    creds = auth.get_credentials()
    clips = twitch.get_clips(creds, game_name='dota 2')
    print(clips)


if __name__ == "__main__":
    main()