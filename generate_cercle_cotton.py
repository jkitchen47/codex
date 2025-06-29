import os
import requests
from moviepy.editor import (ImageClip, VideoFileClip, AudioFileClip,
                            concatenate_videoclips, CompositeVideoClip, vfx)
from PIL import Image
from io import BytesIO

# Step 2: Download images from Unsplash API
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")  # Set your key as an env var
HEADERS = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
query = "mayan temple jungle sunrise"  # Choose a scenic location
url = f"https://api.unsplash.com/search/photos?query={query}&per_page=3"
response = requests.get(url, headers=HEADERS)
response.raise_for_status()
results = response.json()['results']
image_paths = []

for i, r in enumerate(results):
    image_url = r['urls']['regular']
    img_data = requests.get(image_url).content
    path = f"image_{i}.jpg"
    with open(path, 'wb') as f:
        f.write(img_data)
    image_paths.append(path)

# Optional: download a stock video clip for drone footage via Pexels or another source.
# This example assumes we have a local 'drone.mp4' clip.
drone_clip = VideoFileClip('drone.mp4').subclip(0, 10)  # first 10 seconds

image_clips = []
for path in image_paths:
    img = Image.open(path)
    # Use Ken Burns effect via resize and pan
    clip = ImageClip(path).set_duration(5).resize(width=1920)
    clip = clip.fx(vfx.crop, x1=0, y1=50, x2=1920, y2=1030).fx(vfx.fadein, 1)
    image_clips.append(clip)

# Step 4: Insert performer clip (e.g., fiddler on green screen)
performer = VideoFileClip('performer.mp4').subclip(0, 15)
# Optionally apply chroma key here to composite
# For simplicity, we overlay performer in center for last image clip
last_bg = image_clips[-1].set_duration(performer.duration)
composite = CompositeVideoClip([last_bg, performer.set_position('center')])

# Concatenate clips with drone and images
sequence = [drone_clip] + image_clips[:-1] + [composite]
video = concatenate_videoclips(sequence, method='compose')

# Step 5: Overlay audio track
audio = AudioFileClip('cotton_eyed_joe.mp3')
video = video.set_audio(audio.subclip(0, video.duration))

# Step 6: Add intro and outro fades
video = video.fx(vfx.fadein, 2).fx(vfx.fadeout, 3)

# Export final video
video.write_videofile('cotton_cercle.mp4', fps=24)

