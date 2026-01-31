from youtube_transcript_api import YouTubeTranscriptApi
try:
    ts = YouTubeTranscriptApi.list_transcripts('dQw4w9WgXcQ')
    print("Successfully called .list_transcripts()")
    for t in ts:
        print(f"Transcript language: {t.language}, Code: {t.language_code}, Is generated: {t.is_generated}")
except Exception as e:
    print(f"Error calling .list_transcripts(): {e}")
