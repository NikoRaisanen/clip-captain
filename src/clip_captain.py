#!/bin/python
from moviepy.editor import *
import helpers.twitch as twitch
import helpers.cli as cli
import helpers.youtube as yt
import helpers.video_processing as vid_p
from config import VALID_LANGUAGES


# Data structure for the final video, used to populate information in Youtube Upload API
# TODO: add support for multiple languages...
# Language format will be needed for clip downloading and yt video upload
# TODO: Possibly break video class into multiple specialized classes
class Video:
    """Object to store data about the final video"""
    def __init__(self, game_name, language, title, thumbnail, tags, description, privacy_status, streamers=None, clips=None):
        self.game_name = game_name
        self.title = title
        self.language = language
        self.streamers = streamers
        self.thumbnail = thumbnail
        self.tags = tags
        self.description = description
        self.privacy_status = privacy_status
        self.clips = clips
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
        """Return list of unique streamers"""
        return list(set(self.streamers))

    def set_default_description(self):
        """create default description that credits all content owners"""
        credit = ''
        for streamer in self.streamers:
            link = f'https://www.twitch.tv/{streamer}'
            credit = f'{credit}\n{link}'

        self.description = f"""{self.title}\n
            Make sure to support the streamers in the video!
            {credit}"""
        

def validate_cli_args(args):
    """Validate cli args, bypass if account_id is provided"""
    if args.account_id:
        return
    if not args.game:
        raise ValueError('Game name must be specified with -g or --game')
    if not args.video_title:
        raise ValueError('Video title must be specified with -vt or --video-title')
    if args.language not in VALID_LANGUAGES:
        raise ValueError(f'{args.language} is not supported. Options: {VALID_LANGUAGES}')


def normalize_args(args):
    """Return normalized args"""
    if args.account_id:
        norm = yt.vid_info_from_json(args.account_id)
        return norm
    norm = {
        'game': args.game,
        'numClips': args.num_clips,
        'language': args.language,
        'pastDays': args.past_days,
        'title': args.video_title,
        'tags': args.tags,
        'privacy': args.privacy
    }
    return norm
  

# TODO: Create bash script to automatically run the program for a given user
# TODO: Create wrapper fn for each of the 2 cases below (programmatic vs ad-hoc)
def main():
    args = cli.start()
    validate_cli_args(args)
    na = normalize_args(args)
    twitch_auth = twitch.get_credentials()

    clips = None
    yt_service = None
    creators = None
    vid = None
    if args.account_id:
        yt_service = yt.oauth_flow(args.account_id)
        v = yt.vid_info_from_json(args.account_id)
        clips = twitch.get_clips(twitch_auth, v['language'], v['game'], v['pastDays'], v['numClips'])
        creators = twitch.get_creator_names(clips)
        vid = Video(v['game'], v['language'], v['title'], None, v['tags'], None, v['privacy'], creators, clips)
        vid_path = vid_p.finalize_video(clips, None, vid.filename, v['game'])


    else:
        yt_service = yt.oauth_flow()
        clips = twitch.get_clips(twitch_auth, args.language, args.game, args.past_days, args.num_clips)
        creators = twitch.get_creator_names(clips)
        vid = Video(args.game, args.language,  args.video_title, args.thumbnail, args.tags, args.description, args.privacy_status, creators, clips)
        vid_path = vid_p.finalize_video(clips, args.transition_media, vid.filename, args.game)

    vid.filename = vid_path

    yt.upload_video(yt_service, vid)


if __name__ == "__main__":
    # Sample Usage:
    # python ./src/clip_captain.py -g 'Just Chatting' -n 15 -vt 'Twitch Just Chatting | Best Moments of the Week #1' -t 'just chatting' 'twitch' 'best' 'best of' 'best just chatting' 'twitch just chatting' 'compilation' -p 'public' -pd 7
    main()
