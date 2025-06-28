import os
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from pathlib import Path

# Prompt user for folder path
directory = input("Enter the full path to your MP3 files folder: ").strip()

if not os.path.isdir(directory):
    print("The specified path does not exist. Exiting.")
    exit(1)

# Process each MP3 file
for filename in os.listdir(directory):
    if filename.lower().endswith(".mp3"):
        file_path = os.path.join(directory, filename)
        try:
            audio = ID3(file_path)
            artist = audio.get("TPE1")  # TPE1 is the 'Artist' tag

            if artist:
                artist_name = artist.text[0].strip()
                new_file_path = os.path.join(directory, f"{artist_name}.mp3")

                # Handle duplicate filenames by appending a number
                counter = 1
                while os.path.exists(new_file_path):
                    new_file_path = os.path.join(directory, f"{artist_name} ({counter}).mp3")
                    counter += 1

                os.rename(file_path, new_file_path)
                print(f"Renamed '{filename}' to '{os.path.basename(new_file_path)}'")
            else:
                print(f"No artist tag found for '{filename}' — skipping.")

        except Exception as e:
            print(f"Error reading '{filename}': {e}")

print("\nAll files processed.")
