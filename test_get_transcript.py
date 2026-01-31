from youtube_transcript_api import YouTubeTranscriptApi
try:
    data = YouTubeTranscriptApi.get_transcript('dQw4w9WgXcQ')
    print("Success: get_transcript works")
    print(data[:2])
except AttributeError:
    print("AttributeError: get_transcript does not exist")
except Exception as e:
    print(f"Other Error: {e}")
