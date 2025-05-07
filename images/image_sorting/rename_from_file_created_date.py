import os
from datetime import datetime
import time

# Get the current directory
folder_path = input("Enter the folder path containing webp files: ").strip()
if not os.path.isdir(folder_path):
    raise ValueError("The provided path is not a valid directory.")
# Supported image extensions
image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", "webp")

# ask if user wants to use creation time or modified time
use_creation_time = (
    input("Do you want to use the creation time or modified time? (1/2)? ")
    .strip()
    .lower()
)


# Iterate through files in the current directory
for filename in os.listdir(folder_path):
    # Check if the file is an image
    if filename.lower().endswith(image_extensions):
        # Get the full file path
        file_path = os.path.join(folder_path, filename)

        # Get the creation time
        creation_time = os.path.getctime(file_path)

        # Get the modified time
        modified_time = os.path.getmtime(file_path)

        selected_time = creation_time if use_creation_time == "1" else modified_time

        # Convert to Unix timestamp (milliseconds)
        timestamp_ms = int(selected_time * 1000)

        # Get the file extension
        _, ext = os.path.splitext(filename)

        # Create new filename with timestamp
        new_filename = f"{timestamp_ms}{ext}"
        new_file_path = os.path.join(folder_path, new_filename)

        # Check if the new file name is the same as the old one
        if new_file_path == file_path:
            print(f"File {filename} already has the correct name.")
            continue

        # Handle duplicate timestamps
        counter = 1
        while os.path.exists(new_file_path):
            new_timestamp_ms = timestamp_ms + counter
            new_filename = f"{new_timestamp_ms}{ext}"
            new_file_path = os.path.join(folder_path, new_filename)
            counter += 1

        # Rename the file
        try:
            os.rename(file_path, new_file_path)
            print(f"Renamed: {filename} -> {new_filename}")
        except OSError as e:
            print(f"Error renaming {filename}: {e}")
