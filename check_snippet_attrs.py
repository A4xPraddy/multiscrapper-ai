from youtube_transcript_api import YouTubeTranscriptApi

try:
    yt_api = YouTubeTranscriptApi()
    transcript_list = yt_api.list('dQw4w9WgXcQ')
    transcript = transcript_list.find_transcript(['en'])
    data = transcript.fetch()
    if len(data) > 0:
        first_item = data[0]
        print(f"Attributes of FetchedTranscriptSnippet: {dir(first_item)}")
        print(f"Sample text: {first_item.text}")
except Exception as e:
    print(f"Error: {e}")
