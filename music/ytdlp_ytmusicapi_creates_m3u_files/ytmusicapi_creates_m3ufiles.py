import os
import re
from ytmusicapi import YTMusic

def extract_playlist_id(url):
    match = re.search(r'list=([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else None

def main(txt_file_path, output_folder):
    ytmusic = YTMusic("browser.json")  # Must already be set up
    os.makedirs(output_folder, exist_ok=True)

    with open(txt_file_path, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        playlist_id = extract_playlist_id(url)
        if not playlist_id:
            print(f"Could not extract playlist ID from: {url}")
            continue

        playlist = ytmusic.get_playlist(playlist_id, limit=500)
        playlist_name = playlist['title'].replace('/', '_')  # sanitize file name
        tracks = playlist['tracks']

        out_path = os.path.join(output_folder, f"{playlist_name}.m3u")
        with open(out_path, 'w', encoding='utf-8') as m3u:
            m3u.write("#EXTM3U\n")
            for track in tracks:
                title = track['title']
                artists = ', '.join([a['name'] for a in track['artists']])
                m3u.write(f"#EXTINF:-1,{artists} -- {title}\n")
                m3u.write(f"{title}\n")

        print(f"Saved: {out_path}")

if __name__ == "__main__":
    txt_file_path = input("Path to playlists.txt: ").strip()
    output_folder = input("Output folder for M3U files: ").strip()
    main(txt_file_path, output_folder)
