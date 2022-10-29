import argparse


def start():
    """Get params from cli"""
    parser = argparse.ArgumentParser(description="Automatically create and upload a gaming youtube video")
    parser.add_argument("-g", "--game", type=str, help="Name of target game", required=True)
    parser.add_argument("-pd", "--past-days", type=int, help="Get clips from the past X days", required=False, default=7)
    parser.add_argument("-n", "--num-clips", type=str, help="Number of clips to be used in your video", required=False, default=20)
    parser.add_argument("-f", "--first", type=str, help="Fetch X clips on each Twitch api call", required=False, default=20)
    parser.add_argument("-l", "--language", type=str, help="Language of fetched clips", required=False, default=None)
    args = parser.parse_args()
    return args
