#!/bin/python
import requests, time, json, pprint
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
# Site to download clips: https://clipr.xyz/ 

credentials = []
# Get url of 20 valorant clips

# Get credentials for Twitch api from file
with open('confidential.json', 'r') as fp:
    credentials = json.load(fp)



# WORK API SOLUTION FOR CLIP PROCURING BELOW HERE ***

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

clipDownloadLinks = []
clipUrls = []
clipsAPI = 'https://api.twitch.tv/helix/clips'
PARAMS = {'game_id': 516575, 'started_at': '2021-06-30T10:49:29Z'}
HEADERS = {'Client-Id': credentials['twitch_client_id'], 'Authorization': 'Bearer ' + credentials['access_bearer_token']}
r = requests.get(url=clipsAPI, params=PARAMS, headers=HEADERS)
data = r.json()
pprint.pprint(data)
print(type(data))

# Get link to download each video and put into list
for entry in data['data']:
    clipDownloadLinks.append(entry['thumbnail_url'])

print(clipDownloadLinks)
print(len(clipDownloadLinks))

for link in clipDownloadLinks:
    clipUrls.append(link.split('-preview-')[0] + '.mp4')
    
print(clipUrls)