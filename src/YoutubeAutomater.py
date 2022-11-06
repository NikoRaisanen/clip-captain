#!/bin/python
import requests, json
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
import helpers.cli as cli
import helpers.youtube as yt
import helpers.video_processing as video_helper


YT_CREDS = f'{os.getcwd()}/src/secrets/youtube_creds.json'
# Data structure for the final video, used to populate information in Youtube Upload API
class Video:
    def __init__(self, game_name=None, title=None, thumbnail='', tags=None, description=None, privacy_status='unlisted', streamers=None, clips=None):
        self.game_name = game_name
        self.title = title
        self.streamers = streamers
        self.thumbnail = thumbnail
        self.tags = tags
        self.description = description
        self.privacy_status = privacy_status
        self.clips = clips
        # filename is dynamically set
        self.filename = ''

    def __str__(self):
        return f'''
        Game: {self.game_name}
        Title: {self.title}
        Thumbnail: {self.thumbnail}
        Tags: {self.tags}
        Description: {self.description}
        Creators: {self.streamers}
        Filename: {self.filename}
        '''

    def get_unique_streamers(self):
        return list(set(self.streamers))
  
    def set_default_description(self):
        credit = ''
        for streamer in self.streamers:
            link = f'https://www.twitch.tv/{streamer}'
            credit = f'{credit}\n{link}'

        self.description = f'{self.title}\n\nMake sure to support the streamers in the video!\n{credit}'
          
        
def combine_clips(clips, transition):
    videoObjects = []
    for clip in clips:
        # Add text below:
        video = VideoFileClip(os.path.join(base_path, clip.filename), target_resolution=(1080,1920))
        txt_clip = TextClip(clip.streamerName, fontsize = 60, color = 'white',stroke_color='black',stroke_width=2, font="Fredoka-One")
        txt_clip = txt_clip.set_pos((0.8, 0.9), relative=True).set_duration(video.duration)
        video = CompositeVideoClip([video, txt_clip]).set_duration(video.duration)
        videoObjects.append(video)

    # TODO: check if the custom transition exists
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
    args = cli.start()
    creds = auth.get_credentials()
    clips = twitch.get_clips(creds, args.game, args.past_days, args.num_clips, args.first)
    creators = twitch.get_creator_names(clips)
    vid = Video(args.game, args.video_title, args.thumbnail, args.tags, args.description, args.privacy_status, creators, clips)

    # Go through oauth flow
    yt_service = yt.get_authenticated_service(YT_CREDS)

    # TODO: Add video creation steps here
    vid_path = video_helper.generate_video(clips, args.transition_media, args.game)
    vid.filename = vid_path

    yt.upload_video(yt_service, vid)
    

if __name__ == "__main__":
    main()