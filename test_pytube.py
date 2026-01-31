from pytube import YouTube
import os

try:
    print("Testing pytube...")
    yt = YouTube('https://www.youtube.com/watch?v=Cjp6RVrOOW0')
    print(f"Title: {yt.title}")
    audio_stream = yt.streams.filter(only_audio=True).first()
    if audio_stream:
        print(f"Audio stream found: {audio_stream}")
        # Don't download yet, just checking connectivity
    else:
        print("No audio stream found.")
except Exception as e:
    print(f"Pytube error: {e}")
