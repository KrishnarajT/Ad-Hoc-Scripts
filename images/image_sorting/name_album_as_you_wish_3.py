import os
from mutagen.id3 import ID3, TALB
from pathlib import Path
import shutil

# Prompt for base directory containing subfolders
base_directory = input("Enter the full path to your base folder: ").strip()

if not os.path.isdir(base_directory):
    print("The specified path does not exist. Exiting.")
    exit(1)

# Walk through the directory tree
for root, dirs, files in os.walk(base_directory):
    mp3_files = [f for f in files if f.lower().endswith(".mp3")]

    # Only process folders containing MP3 files
    if mp3_files:
        album_name = os.path.basename(root)
        print(f"\nProcessing folder: {root} | Album: {album_name}")

        for filename in mp3_files:
            original_file = os.path.join(root, filename)
            updated_file = os.path.join(root, f"{Path(filename).stem}_updated.mp3")

            # Copy original to new file
            shutil.copy2(original_file, updated_file)

            try:
                audio = ID3(updated_file)

                # Set the album tag
                audio.setall("TALB", [TALB(encoding=3, text=album_name)])
                audio.save()

                print(f"  Set album tag for: {filename}")

                # Remove the original file
                os.remove(original_file)

                # Rename updated file to original filename
                os.rename(updated_file, original_file)

                print(f"  Replaced original file: {filename}")

            except Exception as e:
                print(f"  Error processing '{filename}': {e}")

print("\nAll files processed.")
