import os
from mutagen.id3 import ID3, TALB
from mutagen.mp3 import MP3
from pathlib import Path
import shutil

# Prompt for folder path and album name
directory = input("Enter the full path to your MP3 files folder: ").strip()
album_name = input("Enter the album name to set for all MP3 files: ").strip()

if not os.path.isdir(directory):
    print("The specified path does not exist. Exiting.")
    exit(1)

# Process each MP3 file
for filename in os.listdir(directory):
    if filename.lower().endswith(".mp3"):
        original_file = os.path.join(directory, filename)
        updated_file = os.path.join(directory, f"{Path(filename).stem}_updated.mp3")

        # Copy original to new file (so we don't overwrite)
        shutil.copy2(original_file, updated_file)

        try:
            audio = ID3(updated_file)

            # Set the album tag
            audio.setall("TALB", [TALB(encoding=3, text=album_name)])
            audio.save()

            print(f"Set album tag for: {os.path.basename(updated_file)}")

        except Exception as e:
            print(f"Error processing '{filename}': {e}")

print("\nAll files processed.")
