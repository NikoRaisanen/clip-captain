#!/bin/python
import requests, time, json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
# Site to download clips: https://clipr.xyz/ 

credentials = []
# Get url of 20 valorant clips
# """Without loading dynamic content the following code pulls
# the url of 20 clips. If more clips are needed, make the selenium webdriver 
# scroll to the bottom of the page to load dynamic content"""
clipsList = []
clipsUrl = 'https://www.twitch.tv/directory/game/VALORANT/clips?range=7d'
driver = webdriver.Firefox(executable_path='./geckodriver')

driver.get(clipsUrl)
time.sleep(5)
html = driver.page_source
driver.close()

soup = BeautifulSoup(html, 'html.parser')

for link in soup.find_all('a'):
    if '/clip/' in link.get('href'):
        clipsList.append('twitch.tv' + link.get('href'))
            
# Remove duplicate links
clipsList = list(dict.fromkeys(clipsList))

# GETTING A LIST OF CLIP URLS COMPLETE
print('*' * 20 + 'program finished' + '*' * 20)
print(f'Here is the list of clips:\n {clipsList}')
print(len(clipsList))
for item in clipsList:
    print(item)

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

clipsAPI = 'https://api.twitch.tv/helix/clips'
PARAMS = {'game_id': 516575, 'started_at': '2021-06-30T10:49:29Z'}
HEADERS = {'Client-Id': credentials['twitch_client_id'], 'Authorization': 'Bearer ' + credentials['access_bearer_token']}
r = requests.get(url=clipsAPI, params=PARAMS, headers=HEADERS)
data = r.json()
print(data)