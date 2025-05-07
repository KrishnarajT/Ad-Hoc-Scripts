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
                tracks.append({
                    'name': track['name'],
                    'url': track['external_urls']['spotify'],
                    'artist': ', '.join([a['name'] for a in track['artists']])
                })
            except Exception as e:
                print(f"Error processing track: {e}")
        results = sp.next(results)
    return tracks

playlists = get_user_playlists(sp)
for pl in playlists:
    print(f"Playlist: {pl['name']} — {pl['url']}")
    tracks = get_playlist_tracks(sp, pl['id'])
    for tr in tracks:
        print(f"  - {tr['name']} by {tr['artist']} — {tr['url']}")
