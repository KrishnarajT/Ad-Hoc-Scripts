import json
from ytmusicapi import YTMusic

# Load the authenticated session
ytmusic = YTMusic("browser.json")

# Get all your playlists
playlists = ytmusic.get_library_playlists(limit=100)

# Collect detailed info
all_data = []

for pl in playlists:
    playlist_id = pl["playlistId"]
    playlist_name = pl["title"]
    playlist_tracks = ytmusic.get_playlist(playlist_id, limit=1000)

    track_data = []
    for track in playlist_tracks["tracks"]:
        try:
            track_info = {
                "title": track.get("title"),
                "videoId": track.get("videoId"),
                "artists": [a["name"] for a in track.get("artists", [])],
                "album": track.get("album", {}).get("name"),
                "duration": track.get("duration"),
                "duration_seconds": track.get("duration_seconds"),
                "likeStatus": track.get("likeStatus"),
                "thumbnails": track.get("thumbnails"),
                "isAvailable": track.get("isAvailable"),
                "feedbackTokens": track.get("feedbackTokens"),
            }
        except Exception as e:
            print(f"Error processing track: {e}")
            track_info = {
                "title": track.get("title"),
                "videoId": track.get("videoId"),
                "artists": [a["name"] for a in track.get("artists", [])],
            }
        track_data.append(track_info)

    all_data.append(
        {
            "playlist_name": playlist_name,
            "playlist_id": playlist_id,
            "track_count": len(track_data),
            "tracks": track_data,
        }
    )

# Save to JSON file
with open("all_my_playlists_data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print("Exported your playlists to my_playlists.json")
