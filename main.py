#!/bin/python
import requests, time, json
from bs4 import BeautifulSoup
from selenium import webdriver
# Site to download clips: https://clipr.xyz/ 

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

