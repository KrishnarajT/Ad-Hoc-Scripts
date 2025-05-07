from ytmusicapi import YTMusic
import json

ytmusic = YTMusic()

# Search for the song
search_results = ytmusic.search("Dilwale Dulhania Le Jayenge", filter="albums")

parsed_results = json.dumps(search_results[:2], indent=4)
print(parsed_results)

# Get album browseId from the first result
# album_id = search_results[0]['album']['id']
album_id = search_results[0]['browseId']

# Fetch the album contents
album = ytmusic.get_album(album_id)

# List track titles and videoIds
for track in album['tracks']:
    print(f"{track['title']} - https://music.youtube.com/watch?v={track['videoId']}")
    
    
song = ytmusic.get_song("7JnKVPtRqVE")
print(song)
print(f"Title: {song['videoDetails']['title']}")
print(f"Artist(s): {[a['name'] for a in song['videoDetails']['author'].split(',')]}")
