# Automating Youtube Gaming Highlight Channels (Work in Progress)
![Web front-end of the application](https://github.com/NikoRaisanen/Youtube-Automation/blob/main/assets/frontend.png)
## Why was this application created?

On Youtube you can find hundreds of channels that create gaming compilation videos which receive millions of views. With such viewcounts comes the opportunity to monetize through ad revenue and sponsor activations.
Many of these videos are quite basic in nature, the format is as follows:


* Get 5+ minutes of gaming footage, highlights, etc.
* Overlay the name of the original content creator over the video
* Stitch highlights together with a common transition
* **Profit $$$**


With such a simple formula to create this type of video, there must be a way to automate the entire process...

## What this application does
1. Queries Twitch Clips API for the X most popular clips (videos) for the selected game
2. Downloads these clips into a directory called clips
3. A text overlay is added to each clip which contains the the content creator's name
4. These updated clips are edited together with a common "tv static" transition
5. The resulting video is written into a directory called finalVideos
6. The final video is uploaded to YOUR Youtube channel according to the settings specified in the front-end application

Sample of what the resulting videos look like:
**[link to video PoC]**

All of the content for this video was automatically scraped, edited, and uploaded by filling out a simple form and authenticating with a Google account.

## How it works
The project wasn't as straight-forward as it may seem, in the below video I take you through a deeper dive on how the program works under the hood
**[add link to YT video that I will make]**

## Crediting the content owners
This program takes video content from many creators and consolidates it into a single video. Credit to the original creator is given in the following ways:

* A "watermark" with the creator's name is applied on the bottom right of the video while their clip is being played
* The application's auto-generated description provides a link to the Twitch channels of all creators that appeared in the video

### Run this program locally
This program will **not** work if you only clone it. You will need to get API keys for Twitch and Youtube Data API v3. Upon receiving these API keys you can download the respective json files and name them "twitchCreds.json" and "client_secret.json." Put these 2 json files in the root project directory and your API keys will be used to execute the program!
### Use this program as a SaaS model
I deployed this application onto Google App Engine using a production-quality web server (gunicorn) so that it can be used as a SaaS.
Clicking the "Upload Video" on the GCP-hosted application does not work at the moment. I configured the OAuth Flow to work when the program is accessed locally, the OAuth integration for remote connections is a WIP
