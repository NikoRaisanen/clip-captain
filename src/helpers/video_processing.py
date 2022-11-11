import os
import socket
import requests, json
from moviepy.editor import *
from config import *


def add_creator_watermark(clips, game_name):
    """Add creator watermark to their respective video(s)"""
    download_path = os.path.join(CLIP_PATH, game_name)
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
    if not transition:
        transition = DEFAULT_TRANSITION_PATH

    print(f'Using {transition} as the transitioning media')
    # Make transition clip 1 second long and halve the volume
    transition = VideoFileClip(transition).fx(afx.volumex, 0.5)
    transition = transition.subclip(0, -1)
    print('Beginning to concatenate video clips...')
    final = concatenate_videoclips(videos, transition=transition, method='compose')
    
    if not os.path.exists(FINAL_VID_PATH):
        os.mkdir('finalVideos')
    # TODO: explore using more threads to speed up the process
    final.write_videofile(os.path.join(FINAL_VID_PATH, filename), fps=60, bitrate="6000k", threads=2)
    return os.path.join(FINAL_VID_PATH, filename)


def finalize_video(clips, transition, filename, game_name):
    """Add watermark to clips, stitch videos together with transition"""
    videos = add_creator_watermark(clips, game_name)
    return create_video(videos, transition, filename)
