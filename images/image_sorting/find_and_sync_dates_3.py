import os
import re
from datetime import datetime
import piexif
from PIL import Image

def get_date_formats():
    return [
        (r"\d{4}-\d{2}-\d{2}", "%Y-%m-%d"),                     # YYYY-MM-DD
        (r"\d{2}-\d{2}-\d{4}", "%m-%d-%Y"),                     # MM-DD-YYYY
        (r"\d{2}_\d{2}_\d{4}", "%m_%d_%Y"),                     # MM_DD_YYYY
        (r"\d{4}_\d{2}_\d{2}", "%Y_%m_%d"),                     # YYYY_MM_DD
        (r"\d{4}\d{2}\d{2}", "%Y%m%d"),                         # YYYYMMDD
        (r"\d{2}\d{2}\d{4}", "%m%d%Y"),                         # MMDDYYYY
        (r"\d{4}\d{2}\d{2}_\d{2}\d{2}\d{2}", "%Y%m%d_%H%M%S"),  # YYYYMMDD_HHMMSS
        (r"\d{13}", "timestamp_ms"),                            # Unix timestamp (ms)
        (r"\d{10}", "timestamp_s"),                             # Unix timestamp (s)
    ]

def parse_date(date_str, date_format, format_str):
    try:
        if format_str == "timestamp_ms":
            return datetime.fromtimestamp(int(date_str) / 1000.0)
        elif format_str == "timestamp_s":
            return datetime.fromtimestamp(int(date_str))
        else:
            return datetime.strptime(date_str, format_str)
    except (ValueError, TypeError):
        return None

def modify_exif_date(filepath, date):
    try:
        img = Image.open(filepath)
        if img.format not in ['JPEG', 'JPG', 'WEBP', 'PNG']:
            return False

        # Prepare EXIF data
        exif_dict = piexif.load(img.info.get('exif', b'')) if 'exif' in img.info else {}
        date_str = date.strftime("%Y:%m:%d %H:%M:%S")

        # Update EXIF date fields
        if not exif_dict or exif_dict == {'0th': {}, 'Exif': {}, 'GPS': {}, '1st': {}, 'thumbnail': None}:
            exif_dict = {'0th': {}, 'Exif': {}, 'GPS': {}, '1st': {}, 'thumbnail': None}
        
        exif_dict['0th'][piexif.ImageIFD.DateTime] = date_str
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = date_str
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = date_str

        # Handle formats that might not support EXIF
        if img.format in ['WEBP', 'PNG']:
            img.save(filepath)
        else:
            exif_bytes = piexif.dump(exif_dict)
            img.save(filepath, exif=exif_bytes)

        # Update file modification time
        os.utime(filepath, (date.timestamp(), date.timestamp()))
        return True
    except Exception:
        return False

def process_folder(folder_path, date_format, format_str):
    failed_files = []
    processed_files = []
    
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if not os.path.isfile(filepath):
            continue
            
        # Search for date in filename
        date_match = re.search(date_format, filename)
        if date_match:
            date_str = date_match.group()
            date = parse_date(date_str, date_format, format_str)
            if date and modify_exif_date(filepath, date):
                # Prepare new filename
                new_date_str = date.strftime("%Y%m%d_%H%M%S")
                name, ext = os.path.splitext(filename)
                new_filename = f"{new_date_str}{ext}"
                new_filepath = os.path.join(folder_path, new_filename)
                
                # Ensure unique filename
                counter = 1
                while os.path.exists(new_filepath):
                    new_filename = f"{new_date_str}_{counter}{ext}"
                    new_filepath = os.path.join(folder_path, new_filename)
                    counter += 1
                
                # Rename file
                try:
                    os.rename(filepath, new_filepath)
                    processed_files.append(new_filename)
                except Exception:
                    failed_files.append(filename)
            else:
                failed_files.append(filename)
        else:
            failed_files.append(filename)
    
    return failed_files, processed_files

def main():
    folder_path = input("Enter the folder path containing images: ")
    if not os.path.isdir(folder_path):
        print("Invalid folder path")
        return
    
    date_formats = get_date_formats()
    format_examples = [
        "2023-12-25",
        "12-25-2023",
        "12_25_2023",
        "2023_12_25",
        "20231225",
        "12252023",
        "20231225_143022",
        "1431459209866",
        "1431459209"
    ]
    
    print("Select the date format used in image filenames:")
    for i, (_, example) in enumerate(zip(date_formats, format_examples)):
        print(f"{i + 1}. Example: {example}")
    
    try:
        choice = int(input("Enter the number of your choice: ")) - 1
        if choice < 0 or choice >= len(date_formats):
            print("Invalid choice")
            return
    except ValueError:
        print("Invalid input")
        return
    
    date_format, format_str = date_formats[choice]
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