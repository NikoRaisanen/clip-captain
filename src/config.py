import os


# Path to youtube api keys
YT_SECRETS_PATH = os.path.join(os.getcwd(), 'src', 'secrets', 'youtube_creds.json')

# Path to twitch api keys
TWITCH_SECRETS_PATH = os.path.join(os.getcwd(), 'src', 'secrets', 'twitch_creds.json')

# Path to clip download directory
CLIP_PATH = os.path.join(os.getcwd(), 'clips')

# Path to default transition media
DEFAULT_TRANSITION_PATH = os.path.join(os.getcwd(), 'assets', 'tvstatictransition.mp4')

# Path to final video
FINAL_VID_PATH = os.path.join(os.getcwd(), 'finalVideos')

# Language options of twitch clips
VALID_LANGUAGES = ['en', 'es', 'fr', 'ru', 'ko', 'sv', 'pt', 'da']

# Path to state file, used for automated uploads
STATE_PATH = os.path.join(os.getcwd(), 'src', 'state', 'channels.json')

# Max number of clips to use from a single creator. Set to None to use all clips
CLIPS_PER_CREATOR = 1
