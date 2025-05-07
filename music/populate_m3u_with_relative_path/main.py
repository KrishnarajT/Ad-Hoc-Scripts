import os
from fuzzywuzzy import fuzz
import re
from pathlib import Path
import logging
from mutagen import File
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def getTitle(file_path):
    # use mutagen to get title
    audio = File(file_path, easy=True)
    if audio is None:
        return None
    return audio.get("title", [None])[0]

def getArtists(file_path):
    # use mutagen to get artists
    audio = File(file_path, easy=True)
    if audio is None:
        return []

    raw_artists = audio.get("artist", [])
    cleaned_artists = []

    for entry in raw_artists:
        # Split on common separators: ; , /
        parts = [a.strip() for a in re.split(r'[;,/]', entry) if a.strip()]
        cleaned_artists.extend(parts)

    return cleaned_artists

def build_music_cache(playlists_dir, albums_dir):
    """Build a cache of music files from the albums directory."""
    cache = []
    albums_dir = Path(albums_dir).resolve()
    
    logger.info(f"Building cache from albums directory: {albums_dir}")

    for subdir, dirs, files in os.walk(albums_dir):
        for file in files:
            # only consider music files
            if not any(file.lower().endswith(ext) for ext in [".mp3", ".flac"]):
                continue
            print(os.path.join(subdir, file))
            cache.append({
                "path": os.path.join(subdir, file),
                "relative_path": os.path.relpath(os.path.join(subdir, file), start=playlists_dir),
                # use mutagen to extract artist
                "artist": getArtists(os.path.join(subdir, file)),
                "title": getTitle(os.path.join(subdir, file)),
            })
    logger.info(f"Cached {len(cache)} music files")
    return cache

def find_best_match(playlist_artist, playlist_title, cache):
    """Find the best matching music file for a given artist and title."""
    best_match = None
    best_score = -1
    title_threshold = 80  # Minimum fuzzy match score for title
    artist_boost = 20     # Bonus for artist match
    
    for track in cache:
        # Calculate title similarity
        title_score = fuzz.ratio(playlist_title.lower(), track["title"].lower())
        if title_score < title_threshold:
            continue
            
        # Calculate artist similarity (if available)
        artist_score = 0
        if playlist_artist and track["artist"]:
            artist_score = fuzz.ratio(playlist_artist.lower(), track["artist"].lower())
        
        # Combined score: prioritize title match, boost with artist match
        combined_score = title_score + (artist_score * 0.2 if artist_score > 50 else 0)
        
        if combined_score > best_score:
            best_score = combined_score
            best_match = track
    
    return best_match if best_score >= title_threshold else None

def process_m3u_file(m3u_path, albums_dir, cache):
    """Process a single M3U file and update it with relative paths."""
    logger.info(f"Processing M3U file: {m3u_path}")
    with open(m3u_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            new_lines.append(line)
            continue
        
        # Assume format: Artist -- Title
        match = re.match(r"^(.*?)\s*--\s*(.*?)$", line)
        if not match:
            logger.warning(f"Skipping invalid entry (no separator): {line}")
            new_lines.append(line)
            continue
            
        artist, title = match.groups()
        artist = artist.strip()
        title = title.strip()
        
        # Find best match in cache
        match = find_best_match(artist, title, cache)
        if match:
            new_lines.append(match["relative_path"])
            logger.debug(f"Matched '{artist} -- {title}' to {match['relative_path']}")
        else:
            logger.warning(f"No match found for '{artist} -- {title}'")
            new_lines.append(line)  # Keep original if no match
    
    # Write updated M3U file
    with open(m3u_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines) + '\n')
    logger.info(f"Updated M3U file: {m3u_path}")

def main(playlists_dir, albums_dir):
    """Main function to process all M3U files in the playlists directory."""
    playlists_dir = Path(playlists_dir).resolve()
    albums_dir = Path(albums_dir).resolve()
    
    if not playlists_dir.exists():
        logger.error(f"Playlists directory does not exist: {playlists_dir}")
        return
    if not albums_dir.exists():
        logger.error(f"Albums directory does not exist: {albums_dir}")
        return
    
    # Build cache of music files
    cache = build_music_cache(playlists_dir, albums_dir)
    print(cache)
    # Process each M3U file
    # for m3u_file in playlists_dir.glob("*.m3u"):
    #     process_m3u_file(m3u_file, albums_dir, cache)

if __name__ == "__main__":
    # Example usage
    playlists_directory = input("Enter the path to the playlists directory: ").strip()
    albums_directory = input("Enter the path to the albums directory: ").strip()
    main(playlists_directory, albums_directory)