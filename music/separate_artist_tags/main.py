import os
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1
import re
import re
import os
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1

# Known joint artist names
KNOWN_JOINT_ARTISTS = {
    "simon & garfunkel",
    "earth, wind & fire",
    "hall & oates",
    "ike & tina turner",
    "crosby, stills & nash",
    "crosby, stills, nash & young",
    "peter, paul and mary",
    "peter, paul & mary",
    "derek and the dominos",
    "hootie & the blowfish",
    "the mamas and the papas",
    "emerson, lake & palmer",
    "angus & julia stone",
    "she & him",
    "matt and kim",
    "salt-n-pepa",
    "dj jazzy jeff & the fresh prince",
    "gnarls barkley",
    "louis armstrong and ella fitzgerald",
    "booker t. & the m.g.'s",
    "kool & the gang"
}

def normalize(name):
    return name.lower().strip() if name else None
updates = []
skips = []
separators = ['feat.', 'featuring', ' and ', ' & ', ',', '/', '&', ' And ', ' / ', 'with']
def split_artist_string(artist_raw):
    # Define separators in order of priority
    
    artist_clean = artist_raw.strip()
    for sep in separators:
        if sep.lower() in artist_clean.lower():
            # Normalize all to semicolon-based split
            artist_clean = artist_clean.replace(sep, ';')
    # Now safely split
    return [part.strip() for part in artist_clean.split(';') if part.strip()]


def update_artist_tag(file_path, extension):
    try:
        artist_raw = None
        artist_tag = None

        if extension == '.flac':
            audio = FLAC(file_path)
            artist_tag = audio.get('artist', [])
        elif extension == '.mp3':
            audio = MP3(file_path, ID3=ID3)
            artist_tag = audio.get('TPE1', [])

        if not artist_tag:
            print(f"Skipping {file_path}: No artist tag found.")
            return

        artist_raw = artist_tag[0] if isinstance(artist_tag, list) else str(artist_tag)
        artist_norm = normalize(artist_raw)

        if not artist_norm:
            print(f"Skipping {file_path}: Empty artist field.")
            return

        if artist_norm in KNOWN_JOINT_ARTISTS:
            print(f"Skipping {file_path}: '{artist_raw}' is a known joint artist.")
            skips.append(f"Skipping {file_path}: '{artist_raw}' is a known joint artist.")
            return

        if any(sep in artist_raw.lower() for sep in separators):
            artists = split_artist_string(artist_raw)
            new_artist = ';'.join(artists)

            if new_artist != artist_raw:
                print(f"Updating {file_path}:\n  Original: {artist_raw}\n  New:      {new_artist}")
                updates.append(f"Updating {file_path}:\n  Original: {artist_raw}\n  New:      {new_artist}")
                if extension == '.flac':
                    audio['artist'] = new_artist
                elif extension == '.mp3':
                    audio['TPE1'] = TPE1(encoding=3, text=new_artist)
                audio.save()
            else:
                print(f"No update needed for {file_path}.")

        else:
            print(f"No separators found in {file_path}: '{artist_raw}'")



    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    # Define the root folder (modify this path as needed)
    root_folder = input("Enter the root folder path: ")

    # Supported audio file extensions
    audio_extensions = ('.flac', '.mp3')

    # Walk through the directory tree
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            # Check if the file is an audio file
            if file.lower().endswith(audio_extensions):
                file_path = os.path.join(root, file)
                extension = os.path.splitext(file)[1].lower()
                update_artist_tag(file_path, extension)

if __name__ == "__main__":
    main()
    print("\nUpdates:")
    for update in updates:
        print(update)

    print("\nSkips:")
    for skip in skips:
        print(skip)
    print("\nProcessing complete.")