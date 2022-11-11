import os


# Path to youtube api keys
YT_SECRETS_PATH = os.path.join(os.getcwd(), 'src', 'secrets', 'youtube_creds.json') # rename to 

# Path to twitch api keys
TWITCH_SECRETS_PATH = os.path.join(os.getcwd(), 'src', 'secrets', 'twitch_creds.json')

# Path to clip download directory
CLIP_PATH = os.path.join(os.getcwd(), 'clips')

# Path to default transition media
DEFAULT_TRANSITION_PATH = os.path.join(os.getcwd(), 'assets', 'tvstatictransition.mp4')

# Path to final video
FINAL_VID_PATH = os.path.join(os.getcwd(), 'finalVideos')

