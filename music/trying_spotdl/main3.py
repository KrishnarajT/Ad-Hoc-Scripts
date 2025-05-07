import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import signal
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='8b297a63ec67434cb7d55e8160bc8440',
    client_secret='82e54c8ba5de412d8a64c555e8d349cf',
    redirect_uri='http://1.1.1.1:8888/callback',
    scope='playlist-read-private'
))

# Cache to avoid fetching same album multiple times
album_cache = {}

def get_user_playlists(sp):
    playlists = []
    results = sp.current_user_playlists()
    while results:
        for item in results['items']:
            playlists.append({
                'name': item['name'],
                'url': item['external_urls']['spotify'],
                'id': item['id']
            })
        results = sp.next(results)
    return playlists

def get_album_tracks(album_id):
    try:
        album_tracks = sp.album_tracks(album_id)
        detailed_tracks = []
        for item in album_tracks['items']:
            # Get full track object for metadata
            track = sp.track(item['id'])
            artists = [{
                'name': artist['name'],
                'id': artist['id'],
                'url': artist['external_urls']['spotify']
            } for artist in track['artists']]
            detailed_tracks.append({
                'name': track['name'],
                'id': track['id'],
                'url': track['external_urls']['spotify'],
                'duration_ms': track['duration_ms'],
                'explicit': track['explicit'],
                'popularity': track.get('popularity', None),
                'artists': artists
            })
        return detailed_tracks
    except Exception as e:
        print(f"Error fetching album {album_id}: {e}")
        return []

def get_playlist_tracks(sp, playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    while results:
        for item in results['items']:
            try:
                track = item['track']
                if track is None:
                    continue
                album = track['album']
                album_id = album['id']

                # Check album cache
                if album_id in album_cache:
                    full_album_tracks = album_cache[album_id]
                else:
                    full_album_tracks = get_album_tracks(album_id)
                    album_cache[album_id] = full_album_tracks
                    sleep(0.1)  # polite pause for API

                artists = [{
                    'name': artist['name'],
                    'id': artist['id'],
                    'url': artist['external_urls']['spotify']
                } for artist in track['artists']]

                track_info = {
                    'name': track['name'],
                    'id': track['id'],
                    'url': track['external_urls']['spotify'],
                    'duration_ms': track['duration_ms'],
                    'explicit': track['explicit'],
                    'popularity': track.get('popularity', None),
                    'artists': artists,
                    'album': {
                        'name': album['name'],
                        'id': album_id,
                        'release_date': album.get('release_date', 'N/A'),
                        'total_tracks': album.get('total_tracks', 'N/A'),
                        'url': album['external_urls']['spotify'],
                        'tracklist': full_album_tracks
                    }
                }
                tracks.append(track_info)
            except Exception as e:
                print(f"Error processing track: {e}")
        results = sp.next(results)
    return tracks

def build_playlist_data(sp):
    data = {"playlists": []}
    playlists = get_user_playlists(sp)
    for pl in playlists:
        print(f"Fetching tracks for playlist: {pl['name']}")
        tracks = get_playlist_tracks(sp, pl['id'])
        data["playlists"].append({
            "name": pl["name"],
            "url": pl["url"],
            "tracks": tracks
        })
        with open("spotify_playlists_full_album_tracks.json", "a", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        data.clear()  # Clear data to avoid duplication


# Get structured data
build_playlist_data(sp)

# Write to JSON file
with open("spotify_playlists_full_album_tracks.json", "w", encoding="utf-8") as f:
    json.dump(playlist_data, f, ensure_ascii=False, indent=4)

print("Playlist data with full album tracklists written to 'spotify_playlists_full_album_tracks.json'")

//"https://open.spotify.com/album/7womoox7qHyY9P0ydr7XhN"
"https://open.spotify.com/album/1cRbbPxFMpHFeYIkLqqzBo"
"https://open.spotify.com/album/7ydMeYrv8bFFRkkHepoJM4"
"https://open.spotify.com/album/6FgtuX3PtiB5civjHYhc52"
"https://open.spotify.com/album/1JDlLoZugxdneiaTnGyaKr"
"https://open.spotify.com/album/5ySxm9hxBNss01WCL7GLyQ"
"https://open.spotify.com/album/4alO1zj0clrqWUwC4a9rkL"