import requests
import os
import datetime


# Data structure for each individual clip
class Clip:
    # gameName = ''
    def __init__(self, download_link, streamer_name, filename):
        self.download_link = download_link
        self.streamer_name = streamer_name
        self.filename = filename

        
# TODO: Consider printing a mapping of gameId to gameName in console.
def get_game_id(creds, name):
    """Get id from game name for future api calls"""
    games_endpoint = 'https://api.twitch.tv/helix/games'
    PARAMS = {'name': name}
    HEADERS = {'Client-Id': creds['client_id'], 'Authorization': f'Bearer {creds["bearer_access_token"]}'}
    r = requests.get(url=games_endpoint, params=PARAMS, headers=HEADERS)
    resp = r.json()

    try:
        return resp['data'][0]['id']
    except Exception:
        raise KeyError(f'Cannot find game id for {name}, try adding or removing spaces')


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


def get_creator_names(clips):
    return [x.streamer_name for x in clips]


def download_clips(clips, game_name):
    """Download clips"""
    counter = 0
    base_path = os.path.join(os.getcwd(), 'clips')
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    download_path = os.path.join(base_path, game_name)
    if not os.path.exists(download_path):
        os.mkdir(download_path)

    for clip in clips:
        counter += 1
        r = requests.get(clip.download_link, allow_redirects=True)
        with open(os.path.join(download_path, clip.filename), 'wb') as fp:
            fp.write(r.content)
            print(f'Downloading clip {counter} of {len(clips)} to {os.path.join(download_path, clip.filename)}')

    
def get_clips(creds=None, game_name=None, past_days=7, num_clips=20, first=20, language=None):
    """Wrapper function to perform all Twitch functionality"""
    # TODO: This should return array of Clip objects
    # Video object will be created laters
    game_id = get_game_id(creds, game_name)
    clips = get_clip_info(creds, game_id, past_days, num_clips, first, language)
    download_clips(clips, game_name)
    return clips
