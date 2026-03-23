import numpy as np
import cv2
from moviepy.editor import VideoFileClip, concatenate_videoclips
from scipy.io import wavfile
import requests

VIDEO_FILE = "cricket.mp4"
AUDIO_FILE = "audio.wav"
OUTPUT_FILE = "final_highlight.mp4"

SERVER_URL = "http://127.0.0.1:5000/upload"

print("Loading video...")

clip = VideoFileClip(VIDEO_FILE)

print("Extracting audio...")

clip.audio.write_audiofile(AUDIO_FILE)


rate, data = wavfile.read(AUDIO_FILE)

# stereo → mono
if len(data.shape) > 1:
    data = data.mean(axis=1)


print("Detecting audio spikes...")

window_size = rate * 2

audio_events = []

for i in range(0, len(data), window_size):

    volume = np.abs(data[i:i + window_size]).mean()

    if volume > 2000:
        audio_events.append(i / rate)


print("Detecting motion spikes...")

cap = cv2.VideoCapture(VIDEO_FILE)

motion_events = []

ret, prev = cap.read()

prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)

fps = cap.get(cv2.CAP_PROP_FPS)

frame_no = 0

while True:

    ret, frame = cap.read()

    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    diff = cv2.absdiff(prev_gray, gray)

    motion_score = np.sum(diff)

    if motion_score > 8_000_000:
        motion_events.append(frame_no / fps)

    prev_gray = gray

    frame_no += 1


cap.release()


print("Combining highlight events...")

highlight_times = sorted(set(audio_events + motion_events))


highlight_clips = []

for t in highlight_times:

    start = max(0, t - 3)

    end = min(clip.duration, t + 5)

    highlight_clips.append(clip.subclip(start, end))


if not highlight_clips:
    highlight_clips.append(clip.subclip(0, 10))


print("Creating highlight video...")

final_clip = concatenate_videoclips(highlight_clips)

final_clip.write_videofile(
    OUTPUT_FILE,
    codec="libx264",
    audio_codec="aac"
)

print("Uploading highlight video...")

files = {'file': open(OUTPUT_FILE, 'rb')}

response = requests.post(SERVER_URL, files=files)

print("Upload status:", response.text)