import json, requests
from datetime import datetime, timedelta

credentials = ''
with open('confidential.json', 'r') as fp:
        credentials = json.load(fp)

def get_clips_request(first=20, cursor=None):
    game_id = '509659'
    pastDays = 7
    timeNow = datetime.now().isoformat()
    timeNow = timeNow.split('.')[0]
    timeNow = timeNow + "Z"
    timeNow = datetime.strptime(timeNow, '%Y-%m-%dT%H:%M:%SZ')

    # Subtract current time by 7 days to get startDate (lower bounds of date to look for clips)
    startDate = timeNow - timedelta(pastDays)
    startDate = startDate.isoformat()
    startDate = startDate + "Z"

    clipInfo = []
    finalClipInfo = []
    counter = 0
    while len(clipInfo) < 20:
        counter += 1
        print(f'Iteration #{counter}')
        clipsAPI = 'https://api.twitch.tv/helix/clips'
        PARAMS = {'game_id': game_id, 'started_at': startDate, 'first': first, 'after': cursor}
        HEADERS = {'Client-Id': credentials['twitch_client_id'], 'Authorization': 'Bearer ' + credentials['access_bearer_token']}
        r = requests.get(url=clipsAPI, params=PARAMS, headers=HEADERS)
        data = r.json()

        for item in data['data']:
            if item['language'][:2] == 'es':
                print(item)
                clipInfo.append([item['thumbnail_url'], item['broadcaster_name'], item['game_id'], item['language']])
        cursor = data['pagination']['cursor']
    # Convert thumbnail_url to download link and create list with download link, broadcaster_name, game_id
    for link in clipInfo:
        finalClipInfo.append([link[0].split('-preview-')[0] + '.mp4', link[1], link[2], link[3]])
        print(link[3])
    print('done getting clip info')
    print(clipInfo)
    print(len(clipInfo))
    # return finalClipInfo, game_id


get_clips_request()
# Append whole json entry if the language matches
# print(data1)
# for item in data['data']:
#     if item['language'][:2] == 'es':
#         print(item)

# cursor = data['pagination']['cursor']