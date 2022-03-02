import youtube_dl
import ffmpy
from glob import glob
import cv2
import os
import subprocess
from svg.path import parse_path
from svg.path.path import CubicBezier, Line
from xml.dom import minidom
import json
from urllib import request
from os import path

def clear():
    for f in glob('video/frames/*'):
        os.remove(f)
    if path.exists('video/video.mp4'): os.remove('video/video.mp4')
    if path.exists('video/audio.mp3'): os.remove('video/audio.mp3')
    with open('static/frames.json', 'w') as f:
        f.write(r'{}')
    with open('static/settings.json', 'w') as f:
        f.write(r'{"frontend": {"top": "4000","bottom": "0","left": "0","right": "7000","color": "#000000","grid": "false"},"backend": {"L2": "false"}}')

def extract(url):
    #Download the youtube video
    ydl_ops = {
        'outtmpl': 'video/video.%(ext)s',
        'format': 'mp4'
    }
    with youtube_dl.YoutubeDL(ydl_ops) as ydl:
        ydl.download([url])

    #Extract the frames and audio
    ffmpy.FFmpeg(
        inputs={'video/video.mp4': None},
        outputs={
            'video/frames/%d.png': None,
            'video/audio.mp3': '-y'
        }
    ).run()

def format(png, bmp):
    edge_data = cv2.Canny(cv2.imread(png), 100, 200)
    cv2.imwrite(bmp, edge_data)
    subprocess.run(['potrace', bmp, '-s'])

def latex(filename):
    latex = {}
    paths = [path.getAttribute('d') for path in minidom.parse(filename).getElementsByTagName('path')]
    i=0
    for path in paths:
        for segment in parse_path(path):
            if isinstance(segment, Line):
                x0, y0 = segment.start.real, segment.start.imag
                x1, y1 = segment.end.real, segment.end.imag
                latex[i] = f'((1-t){x0}+t{x1},(1-t){y0}+t{y1})'
                i += 1
            elif isinstance(segment, CubicBezier):
                x0, y0 = segment.start.real, segment.start.imag
                x1, y1 = segment.control1.real, segment.control1.imag
                x2, y2 = segment.control2.real, segment.control2.imag
                x3, y3 = segment.end.real, segment.end.imag
                latex[i] = f'((1-t)((1-t)((1-t){x0}+t{x1})+t((1-t){x1}+t{x2}))+t((1-t)((1-t){x1}+t{x2})+t((1-t){x2}+t{x3})),(1-t)((1-t)((1-t){y0}+t{y1})+t((1-t){y1}+t{y2}))+t((1-t)((1-t){y1}+t{y2})+t((1-t){y2}+t{y3})))'
                i += 1
    return latex

def start(url):
    clear()

    #settings = json.load('static/settings.json')['backend']
    #print(settings)

    extract(url)

    for i in range(1, len(glob('video/frames/*.png')) + 1):
        format(f'video/frames/{i}.png', f'video/frames/{i}.bmp')

    render = {}
    for i in range(1, len(glob('video/frames/*.bmp')) + 1):
        render[f'{i}'] = latex(f'video/frames/{i}.svg')

    with open('static/frames.json', 'w') as file:
        json.dump(render, file, indent=4)

frames = []
def save(img):
    data, frame = img['data'], img['frame']
    with request.urlopen(data) as responce:
        with open(f'video/frames/_{frame}.png', 'wb') as file:
            file.write(responce.read())

def to_video():
    ffmpy.FFmpeg(
        inputs={
            'video/frames/_%d.png': '-r 30',
            'video/audio.mp3': None
            },
        outputs={'static/video.mp4': '-pix_fmt yuv420p -r 30 -shortest -y'}
    ).run()
    