from time import time
import requests
import json
import os
import datetime
import auth

# Possibly use dropdown on front-end to get the gameName
# Consider printing a mapping of gameId to gameName in console.
def get_game_id(name, creds):
    games_endpoint = 'https://api.twitch.tv/helix/games'
    PARAMS = {'name': name}
    HEADERS = {'Client-Id': creds['client_id'], 'Authorization': f'Bearer {creds["bearer_access_token"]}'}
    r = requests.get(url=games_endpoint, params=PARAMS, headers=HEADERS)
    resp = r.json()

    try:
        return resp['data'][0]['id']
    except Exception as e:
        raise KeyError(f'Cannot find game id for {name}, try adding or removing spaces')

# game_id, pastDays, numClips, language <-- all vars declared on program start
def get_clip_info(creds=None, game_id=None, pastDays=7, numClips = 20, first = 50, cursor = None, language=None):
    # TODO: allow multi-language support
    # TODO: allow a custom date range for clips, not only pastDays
    print(f'Language to be used is: {language}')
    # Get current time in RFC3339 format with T and Z
    time_now = datetime.datetime.now()
    start_date = time_now - datetime.timedelta(pastDays)
    start_date = start_date.isoformat('T') + 'Z'

    # STOPPING POINT. All functionality above this line works
    # Call twitch api to get thumbnail url, broadcaster name, game id
    counter = 1
    clips = []


    # Keep paginating through twitch clips API until 20 valid clips
    while len(clips) < numClips:
        print(f'Query #{counter} for valid clips')
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

if __name__ == '__main__':
    creds = auth.get_credentials()
    game_id = get_game_id('dota 2', creds)
    get_clip_info()