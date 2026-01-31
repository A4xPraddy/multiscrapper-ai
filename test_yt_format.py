from youtube_transcript_api import YouTubeTranscriptApi

try:
    yt_api = YouTubeTranscriptApi()
    # Using a common video for testing
    transcript_list = yt_api.list('dQw4w9WgXcQ')
    transcript = transcript_list.find_transcript(['en'])
    data = transcript.fetch()
    print(f"Data type: {type(data)}")
    if len(data) > 0:
        first_item = data[0]
        print(f"Item type: {type(first_item)}")
        print(f"Item attributes/keys: {first_item.keys() if hasattr(first_item, 'keys') else 'No keys'}")
        try:
            print(f"Access via ['text']: {first_item['text']}")
        except Exception as e:
            print(f"Failed ['text']: {e}")
except Exception as e:
    print(f"Main Error: {e}")
