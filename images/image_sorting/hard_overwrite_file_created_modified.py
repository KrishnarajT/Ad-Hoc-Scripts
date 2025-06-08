import os
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import piexif
import win32file
import pywintypes

def set_file_times(filepath, new_date):
    """Set file modification time using os.utime."""
    try:
        timestamp = int(new_date.timestamp())
        os.utime(filepath, (timestamp, timestamp))
    except Exception as e:
        print(f"Failed to set modification time for {filepath}: {e}")

def set_creation_time(filepath, date):
    """Set file creation time using Windows API."""
    try:
        # Convert datetime to Windows FILETIME format
        filetime = pywintypes.Time(date)
        handle = win32file.CreateFile(
            filepath,
            win32file.GENERIC_WRITE,
            win32file.FILE_SHARE_WRITE,
            None,  # SecurityAttributes
            win32file.OPEN_EXISTING,
            win32file.FILE_ATTRIBUTE_NORMAL,
            None  # TemplateFile
        )
        win32file.SetFileTime(handle, filetime, None, None)  # Set creation time
        handle.Close()
    except Exception as e:
        print(f"Failed to set creation time for {filepath}: {e}")

def set_exif_date(filepath, new_date):
    """Set EXIF date for JPEG files."""
    try:
        date_str = new_date.strftime("%Y:%m:%d %H:%M:%S")
        exif_dict = piexif.load(filepath)
        
        # Update relevant EXIF date fields
        exif_dict["0th"][piexif.ImageIFD.DateTime] = date_str
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_str
        exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = date_str
        
        # Save updated EXIF data
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, filepath)
    except Exception as e:
        print(f"Failed to set EXIF date for {filepath}: {e}")

def main():
    # ask user for folder path
    folder_path = input("Enter the folder path containing webp files: ").strip()
    if not os.path.isdir(folder_path):
        raise ValueError("The provided path is not a valid directory.")
    # Get date input from user
    try:
        year = int(input("Enter year (e.g., 2023): "))
        month = int(input("Enter month (1-12): "))
        day = int(input("Enter day (1-31): "))
        new_date = datetime(year, month, day)
    except ValueError as e:
        print(f"Invalid date input: {e}")
        return

    # Process all files in current directory
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if filename.lower().endswith(('.jpg', '.jpeg')):
            print(f"Processing {filename}...")
            # Set file system timestamps
            set_creation_time(filepath, new_date)
            set_file_times(filepath, new_date)
            # # Set EXIF data for JPEG files
            set_exif_date(filepath, new_date)
            
        elif filename.lower().endswith(('.png', '.gif', '.bmp', '.webp')):
            print(f"Processing {filename}...")
            
            # Set only file system timestamps for non-JPEG images
            set_creation_time(filepath, new_date)
            set_file_times(filepath, new_date)

        # if file is a video
        elif filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '')):
            print(f"Processing {filename}...")
            # Set file system timestamps for video files
            set_creation_time(filepath, new_date)
            set_file_times(filepath, new_date)

        else:
            print(f"Skipping unsupported file type: {filename}")
if __name__ == "__main__":
    main()