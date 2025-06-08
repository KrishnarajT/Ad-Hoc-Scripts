import os
import re
from datetime import datetime
import piexif
from PIL import Image
import pywintypes
import win32file
from tqdm import tqdm

DATE_FORMATS = [
    (r"(20\d{2})-(\d{2})-(\d{2})", "%Y-%m-%d"),  # YYYY-MM-DD (2000+)
    (r"(20\d{2})(\d{2})(\d{2})", "%Y%m%d"),  # YYYYMMDD (2000+)
    (r"(\d{2})-(\d{2})-(20\d{2})", "%d-%m-%Y"),  # DD-MM-YYYY (2000+)
    (r"(\d{2})/(\d{2})/(20\d{2})", "%d/%m/%Y"),  # DD/MM/YYYY (2000+)
    (r"(20\d{2})/(\d{2})/(\d{2})", "%Y/%m/%d"),  # YYYY/MM/DD (2000+)
    (r"(\d{2})(\d{2})(20\d{2})", "%d%m%Y"),  # DDMMYYYY (2000+)
    (r"(\d{1,2})-(\w{3})-(20\d{2})", "%d-%b-%Y"),  # D-MMM-YYYY (2000+)
    (r"(\w{3})\s+(\d{1,2}),\s+(20\d{2})", "%b %d, %Y"),  # Mon DD, YYYY (2000+)
    (r"(\d{1,2})\s+(\w{3})\s+(20\d{2})", "%d %b %Y"),  # DD Mon YYYY (2000+)
    (r"(20\d{2})_(\d{2})_(\d{2})", "%Y_%m_%d"),  # YYYY_MM_DD (2000+)
    (r"(\d{2})_(\d{2})_(20\d{2})", "%d_%m_%Y"),  # DD_MM_YYYY (2000+)
    (r"\d{4}-\d{2}-\d{2}", "%Y-%m-%d"),  # YYYY-MM-DD
    (r"\d{2}-\d{2}-\d{4}", "%m-%d-%Y"),  # MM-DD-YYYY
    (r"\d{2}_\d{2}_\d{4}", "%m_%d_%Y"),  # MM_DD_YYYY
    (r"\d{4}_\d{2}_\d{2}", "%Y_%m_%d"),  # YYYY_MM_DD
    (r"\d{4}\d{2}\d{2}", "%Y%m%d"),  # YYYYMMDD
    (r"\d{2}\d{2}\d{4}", "%m%d%Y"),  # MMDDYYYY
    (r"\d{4}\d{2}\d{2}_\d{2}\d{2}\d{2}", "%Y%m%d_%H%M%S"),  # YYYYMMDD_HHMMSS
    (r"\d{4}\d{2}\d{2}\d{2}\d{2}\d{2}", "%Y%m%d%H%M%S"),  # YYYYMMDDHHMMSS
    (r"\d{13}", "timestamp_ms"),  # Unix timestamp (ms)
    (r"\d{10}", "timestamp_s"),  # Unix timestamp (s)
    (r"\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}", "%Y-%m-%d-%H-%M-%S"),  # YYYY-MM-DD-HH-MM-SS
    (r"\d{4}\d{2}\d{2}-\d{2}\d{2}\d{2}", "%Y%m%d-%H%M%S"),  # YYYYMMDD-HHMMSS
]
FORMAT_EXAMPLES = [
    "2023-12-25 (Format: YYYY-MM-DD)",
    "20231225 (Format: YYYYMMDD)",
    "25-12-2023 (Format: DD-MM-YYYY)",
    "25/12/2023 (Format: DD/MM/YYYY)",
    "2023/12/25 (Format: YYYY/MM/DD)",
    "25122023 (Format: DDMMYYYY)",
    "25-Dec-2023 (Format: D-MMM-YYYY)",
    "Dec 25, 2023 (Format: Mon DD, YYYY)",
    "25 Dec 2023 (Format: DD Mon YYYY)",
    "2023_12_25 (Format: YYYY_MM_DD)",
    "25_12_2023 (Format: DD_MM_YYYY)",
    "2024-12-25 (Format: YYYY-MM-DD)",
    "12-25-2023 (Format: MM-DD-YYYY)",
    "12_25_2023 (Format: MM_DD_YYYY)",
    "2023_12_25 (Format: YYYY_MM_DD)",
    "20231225 (Format: YYYYMMDD)",
    "12252023 (Format: MMDDYYYY)",
    "20231225_143022 (Format: YYYYMMDD_HHMMSS)",
    "20231225143022 (Format: YYYYMMDDHHMMSS)",
    "1431459209866 (Format: Unix timestamp in ms)",
    "1431459209 (Format: Unix timestamp in s)",
    "2023-12-25-14-30-22 (Format: YYYY-MM-DD-HH-MM-SS)",
    "20231225-143022 (Format: YYYYMMDD-HHMMSS)",
]

def user_inputs():
    folder_path = input("Enter the folder path containing images: ")
    if not os.path.isdir(folder_path):
        print("Invalid folder path")
        return

    print("Select the date format used in image filenames:")
    for i, (_, example) in enumerate(zip(DATE_FORMATS, FORMAT_EXAMPLES)):
        print(f"{i + 1}. Example: {example}")

    try:
        choice = int(input("Enter the number of your choice: ")) - 1
        if choice < 0 or choice >= len(DATE_FORMATS):
            print("Invalid choice")
            return
    except ValueError:
        print("Invalid input")
        return

    date_format, format_str = DATE_FORMATS[choice]
    return folder_path, date_format, format_str

def set_creation_time_win_api(filepath, date):
    """
    Set file creation time using Windows API.
    """
    try:
        filetime = pywintypes.Time(date)
        handle = win32file.CreateFile(
            filepath,
            win32file.GENERIC_WRITE,
            win32file.FILE_SHARE_WRITE,
            None,
            win32file.OPEN_EXISTING,
            win32file.FILE_ATTRIBUTE_NORMAL,
            None,
        )
        win32file.SetFileTime(handle, filetime, None, None)
        handle.Close()
    except Exception as e:
        print(f"Failed to set creation time for {filepath}: {e}")

def parse_date(date_str, format_str):
    try:
        if format_str == "timestamp_ms":
            return datetime.fromtimestamp(int(date_str) / 1000.0)
        elif format_str == "timestamp_s":
            return datetime.fromtimestamp(int(date_str))
        else:
            return datetime.strptime(date_str, format_str)
    except (ValueError, TypeError):
        return None

def get_extension(filepath):
    _, ext = os.path.splitext(filepath)
    return ext.lower()

def modify_exif_and_create_modify_times(filepath, correct_date):
    try:
        set_creation_time_win_api(filepath, correct_date)
        os.utime(filepath, (correct_date.timestamp(), correct_date.timestamp()))

        if get_extension(filepath) in [".jpg", ".jpeg"]:
            try:
                img = Image.open(filepath)
                exif_dict = (
                    piexif.load(img.info.get("exif", b""))
                    if "exif" in img.info
                    else {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
                )
                correct_date_str = correct_date.strftime("%Y:%m:%d %H:%M:%S")
                exif_dict["0th"][piexif.ImageIFD.DateTime] = correct_date_str
                exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = correct_date_str
                exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = correct_date_str
                exif_bytes = piexif.dump(exif_dict)
                img.save(filepath, exif=exif_bytes)
                img.close()
                return True
            except Exception as e:
                print(f"Error modifying {filepath}: {e}")
                return False
        return True
    except Exception as e:
        print(f"Error setting file times for {filepath}: {e}")
        return False
def process_folder(folder_path, date_format, format_str):
    failed_files = []
    processed_files = []

    # Walk through all directories and subdirectories
    all_files = []
    for root, _, files in os.walk(folder_path):
        for filename in files:
            all_files.append((root, filename))

    for root, filename in tqdm(all_files, desc="Processing files"):
        filepath = os.path.join(root, filename)

        date_match = re.search(date_format, filename)
        if date_match:
            date_str = date_match.group()
            date = parse_date(date_str, format_str)

            if date and modify_exif_and_create_modify_times(filepath, date):
                new_date_str = str(int(date.timestamp() * 1000))
                _, ext = os.path.splitext(filename)
                new_filename = f"{new_date_str}{ext}"
                new_filepath = os.path.join(root, new_filename)

                if new_filename == filename:
                    print(f"New filename is the same as original filename for: {filename}, skipping rename.")
                    processed_files.append(os.path.join(root, new_filename))
                    continue

                counter = 1
                while os.path.exists(new_filepath):
                    incremented_timestamp = int(new_date_str) + counter
                    new_filename = f"{incremented_timestamp}{ext}"
                    new_filepath = os.path.join(root, new_filename)
                    counter += 1

                try:
                    os.rename(filepath, new_filepath)
                    processed_files.append(os.path.join(root, new_filename))
                except Exception as e:
                    print(f"Failed to rename {filepath} to {new_filepath}: {e}")
                    failed_files.append(os.path.join(root, filename))
            else:
                print(f"Failed to modify EXIF data or set file times for: {os.path.join(root, filename)}")
                failed_files.append(os.path.join(root, filename))
        else:
            print(f"No date found in filename: {os.path.join(root, filename)}")
            failed_files.append(os.path.join(root, filename))

    return failed_files, processed_files

def main():
    folder_path, date_format, format_str = user_inputs()
    if not folder_path:
        return

    failed_files, processed_files = process_folder(folder_path, date_format, format_str)

    if processed_files:
        print("\nSuccessfully processed and renamed files:")
        for file in processed_files:
            print(file)

    if failed_files:
        print("\nThe following files could not be processed:")
        for file in failed_files:
            print(file)
    else:
        print("\nAll files processed successfully")

if __name__ == "__main__":
    main()