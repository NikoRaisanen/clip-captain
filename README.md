# Automating Youtube Gaming Highlight Channels
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
