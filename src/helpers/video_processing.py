import os
import socket
import requests, json
from moviepy.editor import *


def add_creator_watermark(clips):
    """Add creator watermark to their respective video(s)"""
    download_path = os.path.join(os.getcwd(), 'clips')
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


def create_video(videos, transition, filename):
    """Stitch videos together and save the video to disk"""
    # TODO: abstract `os.path.join(os.getcwd(), 'finalVideos')` to config
    # TODO: check if the custom transition exists... also abstract path to the config file
    if not transition:
        transition = f'{os.getcwd()}/assets/tvstatictransition.mp4'

    print(f'Using {transition} as the transitioning media')
    print('done creating list of video objects')
    # Make transition clip 1 second long and halve the volume
    transition = VideoFileClip(transition).fx(afx.volumex, 0.5)
    transition = transition.subclip(0, -1)
    print('Beginning to concatenate video clips...')
    final = concatenate_videoclips(videos, transition=transition, method='compose')
    
    if not os.path.exists(os.path.join(os.getcwd(), 'finalVideos')):
        os.mkdir('finalVideos')
    # TODO: explore using more threads to speed up the process
    final.write_videofile(os.path.join(os.getcwd(), 'finalVideos', filename), fps=60, bitrate="6000k", threads=2)
    return os.path.join(os.getcwd(), 'finalVideos', filename)


def finalize_video(clips, transition, filename):
    """Add watermark to clips, stitch videos together with transition"""
    videos = add_creator_watermark(clips)
    return create_video(videos, transition, filename)

