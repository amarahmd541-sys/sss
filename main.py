import os
import random
import time
import glob
from flask import Flask, send_from_directory, render_template_string, redirect, url_for
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip, ImageClip, clips_array

app = Flask(__name__)
REACTION_IMAGE = "reaction.jpg"
OUTPUT_FOLDER = "static"

if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مصنع الزعيم شملان</title>
    <style>
        body { font-family: sans-serif; background: #1a1a1a; color: white; text-align: center; padding: 20px; }
        .btn { background: #e50914; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 18px; cursor: pointer; text-decoration: none; display: inline-block; margin: 10px; }
        .video-item { background: #333; margin: 10px auto; padding: 15px; border-radius: 10px; max-width: 600px; display: flex; justify-content: space-between; align-items: center; }
        a { color: #4dabf7; text-decoration: none; }
    </style>
</head>
<body>
    <h1>🎬 مصنع فيديوهات الزعيم</h1>
    <a href="/generate" class="btn">⚡ اصنع فيديو جديد الآن</a>
    <hr>
    <h3>الفيديوهات الجاهزة للتحميل:</h3>
    <div id="list">
        {% for video in videos %}
        <div class="video-item">
            <span>{{ video }}</span>
            <a href="/download/{{ video }}" class="btn" style="background: green; padding: 5px 15px;">تحميل ⬇️</a>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

def check_assets():
    if not os.path.exists(REACTION_IMAGE):
        os.system(f"wget -O {REACTION_IMAGE} https://dummyimage.com/1080x960/000/fff.jpg&text=SHAMLAN+REACTION")

def create_video_logic():
    print("🚀 Start Creating...")
    check_assets()
    ydl_opts = {'format': 'bestvideo[ext=mp4,height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]', 'outtmpl': 'temp_video.%(ext)s', 'quiet': True, 'noplaylist': True, 'geo_bypass': True}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            keys = ['funny moments', 'viral shorts', 'satisfying', 'scary caught on camera']
            info = ydl.extract_info(f"ytsearch1:{random.choice(keys)} shorts", download=True)
            if info['entries']:
                clip = VideoFileClip("temp_video.mp4")
                if clip.duration > 59: clip = clip.subclip(0, 59)
                w, h = 1080, 1920
                img = ImageClip(REACTION_IMAGE).resize(width=w, height=h//2).set_duration(clip.duration)
                vid = clip.resize(width=w)
                if vid.h > h//2: vid = vid.crop(y1=vid.h//2 - h//4, height=h//2)
                final = clips_array([[img], [vid]])
                filename = f"video_{random.randint(1000,9999)}.mp4"
                final.write_videofile(f"{OUTPUT_FOLDER}/{filename}", codec='libx264', audio_codec='aac', preset='medium', bitrate="3000k", fps=30)
                clip.close()
                os.remove("temp_video.mp4")
                return True
    except Exception: return False
    return False

@app.route('/')
def index():
    videos = sorted([f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('.mp4')], reverse=True)
    return render_template_string(HTML_TEMPLATE, videos=videos)

@app.route('/generate')
def generate():
    create_video_logic()
    return redirect(url_for('index'))

@app.route('/download/<path:filename>')
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
