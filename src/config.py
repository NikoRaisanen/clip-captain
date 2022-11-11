import os
# TODO store config-type information here such as
# Path to each credentials file
# Path for clip download
# Path for saving the final video
# Default transition path

# Path to youtube keys
YT_CREDS = os.path.join(os.getcwd(), 'src', 'secrets', 'youtube_creds.json') # rename to YT_SECRET_PATH

# Path to twitch keys
SECRETS_PATH = os.path.join(os.getcwd(), 'src', 'secrets', 'twitch_creds.json') # rename to TWITCH_SECRET_PATH

# Path to clip download directory
download_path = os.path.join(os.getcwd(), 'clips') # rename to CLIP_PATH

# Path to default transition media
DEFAULT_TRANSITION_PATH = os.path.join(os.getcwd(), 'assets', 'tvstatictransition.mp4')