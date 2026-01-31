from youtube_transcript_api import YouTubeTranscriptApi

try:
    yt_api = YouTubeTranscriptApi()
    video_id = 'Cjp6RVrOOW0'
    print(f"Testing video: {video_id}")
    
    # Try listing all transcripts
    try:
        transcript_list = yt_api.list(video_id)
        print("Transcript list retrieved.")
        for t in transcript_list:
            print(f"Language: {t.language}, Code: {t.language_code}, Is Generated: {t.is_generated}")
    except Exception as e:
        print(f"List Error: {e}")

except Exception as e:
    print(f"Main Error: {e}")
