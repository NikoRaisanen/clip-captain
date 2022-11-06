import os
import socket
import requests, json
from datetime import datetime
from moviepy.editor import *


def create_filename(game_name):
    now = datetime.now()
    date = now.strftime("%m-%d-%Y")
    return f'{game_name}_{date}.mp4'


# TODO: Split this into 2 functions. 1 for overlaying text, 1 for generating video
def add_watermark(clips, game):
    """Adds text to the bottom of each clip and returns a list of video objects"""
    download_path = os.path.join(os.getcwd(), 'clips', game)
    videos = []
    # set up the composite video that includes streamer name
    for clip in clips:
        # Add text below:
        video = VideoFileClip(os.path.join(download_path, clip.filename), target_resolution=(1080,1920))
        txt_clip = TextClip(clip.streamer_name, fontsize = 60, color = 'white',stroke_color='black',stroke_width=2, font="Fredoka-One")
        txt_clip = txt_clip.set_pos((0.8, 0.9), relative=True).set_duration(video.duration)
        video = CompositeVideoClip([video, txt_clip]).set_duration(video.duration)
        videos.append(video)
    return videos


def combine_clips(videos, transition, filename):
    # TODO: check if the custom transition exists
    if not transition:
        transition = f'{os.getcwd()}/assets/tvstatictransition.mp4'

    print(f'Using {transition} as the transitioning media')
    print('done creating list of video objects')
    # Make transition clip 1 second long and halve the volume
    transition = VideoFileClip(transition).fx(afx.volumex, 0.5)
    transition = transition.subclip(0, -1)
    # video name based on game
    print('Beginning to concatenate video clips...')
    final = concatenate_videoclips(videos, transition=transition, method='compose')
    # Create finalVideos folder if it doesn't exist
    if not os.path.exists(os.path.join(os.getcwd(), 'finalVideos')):
        os.mkdir('finalVideos')
    final.write_videofile(os.path.join(os.getcwd(), 'finalVideos', filename), fps=60, bitrate="6000k", threads=2)
    return os.path.join(os.getcwd(), 'finalVideos', filename)


def generate_video(clips, transition, game):
    """Combines clips into a video and returns the path to the video"""
    filename = create_filename(game)
    videos = add_watermark(clips, game)
    return combine_clips(videos, transition, filename)

    












# # TODO: Split this into 2 functions. 1 for overlaying text, 1 for generating video
# def combine_clips(clips, transition, filename):
#     download_path = os.path.join(os.getcwd(), 'clips')
#     videos = []
#     # set up the composite video that includes streamer name
#     for clip in clips:
#         # Add text below:
#         video = VideoFileClip(os.path.join(download_path, clip.filename), target_resolution=(1080,1920))
#         txt_clip = TextClip(clip.streamer_name, fontsize = 60, color = 'white',stroke_color='black',stroke_width=2, font="Fredoka-One")
#         txt_clip = txt_clip.set_pos((0.8, 0.9), relative=True).set_duration(video.duration)
#         video = CompositeVideoClip([video, txt_clip]).set_duration(video.duration)
#         videos.append(video)

#     # TODO: check if the custom transition exists
#     if not transition:
#         transition = f'{os.getcwd()}/assets/tvstatictransition.mp4'

#     print(f'Using {transition} as the transitioning media')
#     print('done creating list of video objects')
#     # Make transition clip 1 second long and halve the volume
#     transition = VideoFileClip(transition).fx(afx.volumex, 0.5)
#     transition = transition.subclip(0, -1)
#     # video name based on game
#     print('Beginning to concatenate video clips...')
#     final = concatenate_videoclips(videos, transition=transition, method='compose')
#     # Create finalVideos folder if it doesn't exist
#     if not os.path.exists(os.path.join(os.getcwd(), 'finalVideos')):
#         os.mkdir('finalVideos')
#     final.write_videofile(os.path.join(os.getcwd(), 'finalVideos', filename), fps=60, bitrate="6000k", threads=2)
#     return os.path.join(os.getcwd(), 'finalVideos', filename)