import requests
import os
import json
import datetime
from config import TWITCH_SECRETS_PATH, CLIP_PATH, MAX_TWITCH_API_CALLS

# Data structure for each individual clip
class Clip:
    def __init__(self, download_link, streamer_name, filename):
        self.download_link = download_link
        self.streamer_name = streamer_name
        self.filename = filename


def get_credentials():
    current_creds = {}
    try:
        with open(TWITCH_SECRETS_PATH, 'r', encoding='utf-8') as fp:
            current_creds = json.load(fp)
    except FileNotFoundError:
        raise FileNotFoundError(f'Please define client_id and client_secret in {TWITCH_SECRETS_PATH} to authenticate with the Twitch api')
        
    if not current_creds.get('client_id'):
        raise KeyError(f'No client_id property found in {TWITCH_SECRETS_PATH}')
    if not current_creds.get('client_secret'):
        raise KeyError(f'No client_secret property found in {TWITCH_SECRETS_PATH}')

    # check if bearer token still valid
    if current_creds.get('bearer_access_token'):
        HEADERS = {
                'Authorization': f'Bearer {current_creds["bearer_access_token"]}'
                }
        validate_endpoint = 'https://id.twitch.tv/oauth2/validate'
        r = requests.get(url=validate_endpoint, headers=HEADERS)
        if r.status_code == 200:
            return current_creds
    
    # if oauth token not valid, get a new one
    new_oauth_token = get_oauth_token(current_creds)
    current_creds['bearer_access_token'] = new_oauth_token
    update_bearer(new_oauth_token)
    return current_creds


def update_bearer(bearer):
    """update bearer token in credentials file"""
    print('Generating new bearer access token')
    curr = None
    with open(TWITCH_SECRETS_PATH, 'r') as fp:
        curr = json.load(fp)
    # update dict with new bearer
    curr['bearer_access_token'] = bearer

    # write obj with new bearer to file
    with open(TWITCH_SECRETS_PATH, 'w') as fp:
        json.dump(fp=fp, obj=curr)

def get_oauth_token(creds):
    oauth_endpoint = 'https://id.twitch.tv/oauth2/token'
    PARAMS = {
        'client_id': creds['client_id'],
        'client_secret': creds['client_secret'],
        'grant_type': 'client_credentials'
    }
    r = requests.post(url=oauth_endpoint, params=PARAMS)
    return r.json().get('access_token')


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
def get_clip_info(language, creds=None, game_id=None, past_days=7, num_clips = 20, first = 20, cursor = None):
    """
    Returns list of Clip objects that contains the following info for
    each video clip: filename, download link, and name of creator
    """
    
    # TODO: allow a custom date range for clips, not only pastDays
    print(f'Language to be used is: {language}')
    time_now = datetime.datetime.now()
    start_date = time_now - datetime.timedelta(past_days)
    start_date = start_date.isoformat('T') + 'Z'

    counter = 0
    clips = []
    clips_per_creator = {}

    # Keep paginating through twitch clips API until 20 valid clips
    while len(clips) < num_clips:
        if counter >= MAX_TWITCH_API_CALLS:
            print('Max number of API calls reached')
            break
        counter += 1
        print(f'Query #{counter} for valid clips')
        clipsAPI = 'https://api.twitch.tv/helix/clips'
        PARAMS = {'game_id': game_id, 'started_at': start_date, 'first': first, 'after': cursor}
        HEADERS = {'Client-Id': creds['client_id'], 'Authorization': f'Bearer {creds["bearer_access_token"]}'}
        r = requests.get(url=clipsAPI, params=PARAMS, headers=HEADERS)
        data = r.json()

        for item in data['data']:
            if item['language'] != language:
                continue
            if len(clips) >= num_clips:
                break
            cursor = data['pagination']['cursor']
            creator = item['broadcaster_name']
            if creator not in clips_per_creator:
                clips_per_creator[creator] = 1
            else:
                clips_per_creator[creator] += 1

            filename = f'{creator}{clips_per_creator[creator]}.mp4'
            download_link = f'{item["thumbnail_url"].split("-preview-")[0]}.mp4'
            clip = Clip(download_link, creator, filename)
            clips.append(clip)
    

    print('Done getting clip info...')
    return clips


def get_creator_names(clips):
    return [x.streamer_name for x in clips]


def download_clips(clips, game_name):
    """Download clips to disk"""
    counter = 0
    if not os.path.exists(CLIP_PATH):
        os.mkdir(CLIP_PATH)
    download_path = os.path.join(CLIP_PATH, game_name)
    if not os.path.exists(download_path):
        os.mkdir(download_path)

    for clip in clips:
        counter += 1
        r = requests.get(clip.download_link, allow_redirects=True)
        with open(os.path.join(download_path, clip.filename), 'wb') as fp:
            fp.write(r.content)
            print(f'Downloading clip {counter} of {len(clips)} to {os.path.join(download_path, clip.filename)}')

    
def get_clips(language, creds=None, game_name=None, past_days=7, num_clips=20, first=20):
    """Wrapper function to perform all Twitch functionality"""
    game_id = get_game_id(creds, game_name)
    clips = get_clip_info(language, creds, game_id, past_days, num_clips, first)
    download_clips(clips, game_name)
    return clips
