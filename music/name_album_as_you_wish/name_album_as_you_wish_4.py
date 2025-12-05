import os
import unicodedata
from pathlib import Path
from mutagen.id3 import (
    ID3, ID3NoHeaderError,
    TALB, TPE1, TPE2, TIT2, TRCK, TPOS, TCON, TDRC, TSOA, APIC
)

# --- CONFIG ---
ALBUM_ARTIST_DEFAULT = "Various Artists"
GENRE_DEFAULT = "Soundtrack"
YEAR_DEFAULT = "2024"
# --------------

def normalize(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    return " ".join(text.split())

def extract_track_number(filename: str) -> str:
    base = Path(filename).stem
    digits = ""
    for c in base:
        if c.isdigit():
            digits += c
        else:
            break
    return digits if digits else "1"

def extract_title(filename: str) -> str:
    title = Path(filename).stem
    while title and (title[0].isdigit() or title[0] in ".- "):
        title = title[1:]
    title = title.replace("_", " ").strip()
    return normalize(title)

def extract_original_artist_and_cover(file_path: str):
    """Extract TPE1 and APIC frames before wiping tags."""
    artist = "Unknown Artist"
    covers = []

    try:
        audio = ID3(file_path)

        # Preserve artist
        if "TPE1" in audio:
            artist = normalize(audio["TPE1"].text[0])

        # Preserve all embedded cover art
        for key in audio.keys():
            if key.startswith("APIC"):
                covers.append(audio[key])

    except:
        pass

    return artist, covers

def rewrite_tags(file_path: str, album_name: str, track_num: str, title: str):
    original_artist, original_covers = extract_original_artist_and_cover(file_path)

    # Delete ALL tags first (except APIC stored above)
    try:
        audio = ID3(file_path)
        audio.delete()
        audio.save()
    except ID3NoHeaderError:
        pass

    # Build fresh ID3 tag structure
    audio = ID3()

    # Album-level metadata
    audio.add(TALB(encoding=3, text=album_name))
    audio.add(TPE2(encoding=3, text=ALBUM_ARTIST_DEFAULT))
    audio.add(TPOS(encoding=3, text="1"))
    audio.add(TSOA(encoding=3, text=album_name))

    # Track metadata (preserved artist + new title/track #)
    audio.add(TPE1(encoding=3, text=original_artist))
    audio.add(TIT2(encoding=3, text=title))
    audio.add(TRCK(encoding=3, text=track_num))

    # Optional fields
    if GENRE_DEFAULT:
        audio.add(TCON(encoding=3, text=GENRE_DEFAULT))
    if YEAR_DEFAULT:
        audio.add(TDRC(encoding=3, text=YEAR_DEFAULT))

    # Restore cover art
    for cover in original_covers:
        audio.add(APIC(
            encoding=cover.encoding,
            mime=cover.mime,
            type=cover.type,
            desc=cover.desc,
            data=cover.data
        ))

    audio.save(file_path)

# Ask for folder
base_directory = input("Enter folder path: ").strip()

if not os.path.isdir(base_directory):
    print("Folder does not exist.")
    exit(1)

for root, dirs, files in os.walk(base_directory):
    mp3_files = [f for f in files if f.lower().endswith(".mp3")]
    if not mp3_files:
        continue

    album_name = normalize(os.path.basename(root))
    print(f"\n=== Processing Album Folder: {album_name} ===")

    for filename in mp3_files:
        full_path = os.path.join(root, filename)
        print(f"→ {filename}")

        track_num = extract_track_number(filename)
        title = extract_title(filename)

        rewrite_tags(full_path, album_name, track_num, title)

print("\nAll songs cleaned, normalized, and cover art preserved.")
