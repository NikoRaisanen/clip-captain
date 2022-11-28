#!/bin/python
from moviepy.editor import *
import helpers.twitch as twitch
import helpers.cli as cli
import helpers.youtube as yt
import helpers.video_processing as vid_p
from config import VALID_LANGUAGES


# Data structure for the final video, used to populate information in Youtube Upload API
# TODO: add support for multiple languages... Language format will be needed for clip downloading and yt video upload
class Video:
    def __init__(self, game_name, language, title, thumbnail, tags, description, privacy_status, streamers=None, clips=None):
        """Object to store data about the final video"""
        self.game_name = game_name
        self.title = title
        self.language = language
        self.streamers = streamers
        self.thumbnail = thumbnail
        self.tags = tags
        self.description = description
        self.privacy_status = privacy_status
        self.clips = clips
        # filename is dynamically set
        self.filename = f'{game_name}.mp4'

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
        """create default description that credits all content owners"""
        credit = ''
        for streamer in self.streamers:
            link = f'https://www.twitch.tv/{streamer}'
            credit = f'{credit}\n{link}'

        self.description = f'{self.title}\n\nMake sure to support the streamers in the video!\n{credit}'


def validate_language(language):
    if language not in VALID_LANGUAGES:
        raise ValueError(f'Language {language} is not supported. Please use one of the following: {VALID_LANGUAGES}')
        

def main():
    args = cli.start()
    validate_language(args.language)
    creds = twitch.get_credentials()

    # Go through oauth flow before fetching clips
    yt_service = yt.get_authenticated_service()
    clips = twitch.get_clips(args.language, creds, args.game, args.past_days, args.num_clips, args.first)
    creators = twitch.get_creator_names(clips)
    # def __init__(self, game_name, language, title, thumbnail, tags, description, privacy_status, streamers=None, clips=None):
    vid = Video(args.game, args.language,  args.video_title, args.thumbnail, args.tags, args.description, args.privacy_status, creators, clips)
    print(vid)

    vid_path = vid_p.finalize_video(clips, args.transition_media, vid.filename, args.game)
    vid.filename = vid_path

    yt.upload_video(yt_service, vid)
    
    ### Games to start automating
    # OW 2 (multiple languages)
    # Call of Duty
    # Crypto

if __name__ == "__main__":
    main()