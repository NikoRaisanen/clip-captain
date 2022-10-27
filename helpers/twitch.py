from time import time
import requests
import json
import os
import datetime
import auth


# Data structure for the final video, used to populate information in Youtube Upload API
class Video:
    def __init__(self, game_name, filename, title, thumbnail, tags=None, description=None, privacy_status='unlisted', streamers=None, clips=None):
        self.game_name = game_name
        self.filename = filename
        self.title = title
        self.streamers = streamers
        self.thumbnail = thumbnail
        self.tags = tags
        self.description = description
        self.privacy_status = privacy_status
        self.clips = clips

    def __str__(self):
        return f'{self.game_name}\n{self.filename}\n{self.title}\n{self.thumbnail}\n{self.tags}\n{self.description}\n{self.streamers}'

    def get_unique_streamers(self):
        self.streamers = list(set(self.streamers))
  
    def set_default_description(self):
        credit = ''
        for streamer in self.streamers:
            link = f'https://www.twitch.tv/{streamer}'
            credit = f'{credit}\n{link}'

        self.description = f'{self.title}\n\nMake sure to support the streamers in the video!\n{credit}'
          

# Data structure for each individual clip
class Clip:
    # gameName = ''
    def __init__(self, download_link, streamer_name, filename):
        self.download_link = download_link
        self.streamer_name = streamer_name
        self.filename = filename

        
# Possibly use dropdown on front-end to get the gameName
# Consider printing a mapping of gameId to gameName in console.
def get_game_id(creds, name):
    games_endpoint = 'https://api.twitch.tv/helix/games'
    PARAMS = {'name': name}
    HEADERS = {'Client-Id': creds['client_id'], 'Authorization': f'Bearer {creds["bearer_access_token"]}'}
    r = requests.get(url=games_endpoint, params=PARAMS, headers=HEADERS)
    resp = r.json()

    try:
        return resp['data'][0]['id']
    except Exception:
        raise KeyError(f'Cannot find game id for {name}, try adding or removing spaces')


# game_id, pastDays, numClips, first, language <-- all vars declared on program start
# first param must be <= 50
def get_clip_info(creds=None, game_id=None, past_days=7, num_clips = 20, first = 20, cursor = None, language=None):
    """
    Returns list of Clip objects that contains the following info for
    each video clip: filename, download link, and name of creator
    """
    # TODO: allow multi-language support
    # TODO: allow a custom date range for clips, not only pastDays
    print(f'Language to be used is: {language}')
    # Get current time in RFC3339 format with T and Z
    time_now = datetime.datetime.now()
    start_date = time_now - datetime.timedelta(past_days)
    start_date = start_date.isoformat('T') + 'Z'

    counter = 0
    clips = []
    clips_per_creator = {}

    # Keep paginating through twitch clips API until 20 valid clips
    while len(clips) < num_clips:
        counter += 1
        print(f'Query #{counter} for valid clips')
        clipsAPI = 'https://api.twitch.tv/helix/clips'
        PARAMS = {'game_id': game_id, 'started_at': start_date, 'first': first, 'after': cursor}
        HEADERS = {'Client-Id': creds['client_id'], 'Authorization': f'Bearer {creds["bearer_access_token"]}'}
        r = requests.get(url=clipsAPI, params=PARAMS, headers=HEADERS)
        data = r.json()


        # Take the top 20 clips returned by clips api
        if language is None:
            for item in data['data']:
                cursor = data['pagination']['cursor']
                # consider reversing logic. guard clause to break out of loop might be cleaner
                if len(clips) < num_clips:
                    creator = item['broadcaster_name']
                    if creator not in clips_per_creator:
                        clips_per_creator[creator] = 1
                    else:
                        clips_per_creator[creator] += 1

                    filename = f'{creator}{clips_per_creator[creator]}.mp4'
                    download_link = f'{item["thumbnail_url"].split("-preview-")[0]}.mp4'
                    clip = Clip(download_link, creator, filename)
                    clips.append(clip)
        else:
            raise Exception('Language options are not yet supported in this program')

    print('Done getting clip info...')
    return clips


# def download_clips(clips, videoStruct):
#     counter = 0
#     global downloadPath
#     basePath = os.path.join(os.getcwd(), 'clips')
#     if not os.path.exists(basePath):
#         os.mkdir(basePath)
#     downloadPath = os.path.join(basePath, Clip.gameName)
#     if not os.path.exists(downloadPath):
#         os.mkdir(downloadPath)

#     for clip in clips:
#         r = requests.get(clip.downloadLink, allow_redirects=True)
#         videoStruct.streamers.append(clip.streamerName)
#         with open(os.path.join(downloadPath, clip.filename), 'wb') as fp:
#             try:
#                 fp.write(r.content)
#                 print(f'Downloading clip {str(counter + 1)} of {len(clips)} to {os.path.join(downloadPath, clip.filename)}')
#             except:
#                 print("except block executed")

#         counter += 1
#     videoStruct.unique_streamers()
#     print(f'Here are the unique streamers:\n{videoStruct.streamers}')
#     print(f'Finished downloading {counter} clips for {Clip.gameName}!')

def get_clips(creds=None, game_name=None, past_days=7, num_clips=20, first=20):
    """Wrapper function to perform all helpers"""
    # TODO: This should return array of Clip objects
    # Video object will be created later
    # vid = Video()
    game_id = get_game_id(creds, game_name)
    clips = get_clip_info(creds, game_id, past_days, num_clips, first)
    return clips


if __name__ == '__main__':
    creds = auth.get_credentials()
    clips = get_clips(creds, game_name='dota 2')
    print(clips)
    print(len(clips))