from youtube_transcript_api import YouTubeTranscriptApi
try:
    api = YouTubeTranscriptApi()
    ts_list = api.list('dQw4w9WgXcQ')
    print("Success calling api.list()")
    print(ts_list)
except Exception as e:
    print(f"Error: {e}")
