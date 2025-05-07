import os
import json
import yt_dlp
from pathlib import Path
import os
import re
from ytmusicapi import YTMusic
import random 
def extract_playlist_id(url):
    match = re.search(r'list=([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else None

def get_playlist_name(url):
    ytmusic = YTMusic("browser.json")  # Must already be set up

    playlist_id = extract_playlist_id(url)
    if not playlist_id:
        print(f"Could not extract playlist ID from: {url}")
        return random.randint(100000, 999999)  # Fallback to random ID

    playlist = ytmusic.get_playlist(playlist_id, limit=500)
    playlist_name = playlist['title'].replace('/', '_')  # sanitize file name

    return playlist_name

def sanitize(name):
    return "".join(c for c in name if c.isalnum() or c in " _-").strip()

def download_song(url, playlist_name, base_dir="Playlists"):

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{playlist_name}/%(title)s.%(ext)s',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            },
            {
                'key': 'FFmpegMetadata',
            },
            {
                'key': 'EmbedThumbnail',
            }
        ],
        'writethumbnail': True,
        'embedthumbnail': True,
        'embedmetadata': True,
        'prefer_ffmpeg': True,
        'paths': {'home': base_dir},
        'quiet': False,
        'noplaylist': True,
        'cookiefile': r'C:\Users\Krishnaraj\Downloads\cookies.txt',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"❌ Failed to download {url} — {e}")
        return False

if __name__ == "__main__":
    input_file = "playlists.json"

    if not os.path.exists(input_file):
        print(f"⚠️ JSON file not found: {input_file}")
        exit(1)

    with open(input_file, "r") as f:
        playlists = json.load(f)

    print(playlists)
    for playlist_url, tracks in playlists.items():
        playlist_id = playlist_url[-10:]
        print(f"\n🎧 Downloading {len(tracks)} tracks from playlist: {playlist_url}")
        playlist_url = get_playlist_name(playlist_url)
        for url in tracks:
            print(f"➡️  Downloading: {url}")
            success = download_song(url, playlist_url, base_dir=f"Playlists/")
            if success:
                print("✅ Success")
            else:
                print("⚠️ Skipped due to error")

    print("\n✅ All done. Check the Downloads folder.")
