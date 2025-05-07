import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='3af2a5d27e904e91bf4363fe0fa6f2cf',
    client_secret='ff92eef1b3d340989cafe99035762b1d',
    redirect_uri='http://localhost:8888/callback',
    scope='playlist-read-private'
))

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
                    'album': {
                        'name': album['name'],
                        'id': album['id'],
                        'release_date': album.get('release_date', 'N/A'),
                        'total_tracks': album.get('total_tracks', 'N/A'),
                        'url': album['external_urls']['spotify']
                    },
                    'artists': artists
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
        tracks = get_playlist_tracks(sp, pl['id'])
        data["playlists"].append({
            "name": pl["name"],
            "url": pl["url"],
            "tracks": tracks
        })
    return data

# Get structured data
playlist_data = build_playlist_data(sp)

# Write to JSON file
with open("spotify_playlists_full.json", "w", encoding="utf-8") as f:
    json.dump(playlist_data, f, ensure_ascii=False, indent=4)

print("Full playlist metadata written to 'spotify_playlists_full.json'")