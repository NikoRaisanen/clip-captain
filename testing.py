import time, json
from datetime import datetime, timedelta
import requests

# Get current time in RFC3339 format with T and Z
timeNow = datetime.now().isoformat()
timeNow = timeNow.split('.')[0]
timeNow = timeNow + "Z"
timeNow = datetime.strptime(timeNow, '%Y-%m-%dT%H:%M:%SZ')

# Subtract current time by 7 days to get startDate (lower bounds of date to look for clips)
startDate = timeNow - timedelta(days=7)
startDate = startDate.isoformat()
startDate = startDate + "Z"
# Example of startDate variable:
# 2021-06-28T10:53:47Z
# Use startData var for started_at query parameter for twitch clip api calls
credentials = []
with open('confidential.json', 'r') as fp:
    credentials = json.load(fp)

HEADERS = {'Client-Id': credentials['twitch_client_id'], 'Authorization': 'Bearer ' + credentials['access_bearer_token']}
r = requests.get('https://clips-media-assets2.twitch.tv/AT-cm%7C1239511811.mp4', allow_redirects=True)

with open('clip1.mp4', 'wb') as fp:
    fp.write(r.content)