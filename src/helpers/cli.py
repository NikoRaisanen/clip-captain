import argparse
from secrets import choice


def start():
    """Get params from cli"""
    # Params for Twitch api and clip download
    parser = argparse.ArgumentParser(description="Automatically create and upload a gaming youtube video")
    parser.add_argument("-g", "--game", type=str, help="Name of target game", required=True)
    parser.add_argument("-pd", "--past-days", type=int, help="Get clips from the past X days", required=False, default=7)
    parser.add_argument("-n", "--num-clips", type=int, help="Number of clips to be used in your video", required=False, default=20)
    parser.add_argument("-f", "--first", type=int, help="Fetch X clips on each Twitch api call", required=False, default=20)
    parser.add_argument("-l", "--language", type=str, help="Language of fetched clips", required=False, default=None)

    # Params for Youtube Video
    parser.add_argument("-vt", "--video-title", type=str, help="Title of your Youtube video", required=True)
    parser.add_argument("-tn", "--thumbnail", type=str, help="Path to the thumbnail of your video", required=False, default='')
    parser.add_argument("-t", "--tags", type=str, help="Tags for your Youtube video", required=False, default=None)
    parser.add_argument("-d", "--description", type=str, help="Description for your Youtube video", required=False, default=None)
    parser.add_argument("-p", "--privacy-status", type=str, help="Privacy status for your Youtube Video", required=False, default='private', choices=['unlisted', 'private', 'public'])
    parser.add_argument("-tm", "--transition-media", type=str, help="Language of fetched clips", required=False, default=None)

    args = parser.parse_args()
    print(args)
    return args
