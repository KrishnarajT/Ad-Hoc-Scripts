import os
import re
from datetime import datetime
from PIL import Image
import piexif

# 📌 Folder containing images
folder_path = "."

# 📌 Possible date regex patterns and their corresponding strptime formats
date_formats = {
    r"\d{4}-\d{2}-\d{2}": "%Y-%m-%d",
    r"\d{4}\d{2}\d{2}": "%Y%m%d",
    r"\d{2}-\d{2}-\d{4}": "%d-%m-%Y",
    r"\d{2}\d{2}\d{4}": "%d%m%Y",
    r"\d{4}_\d{2}_\d{2}": "%Y_%m_%d",
    r"\d{8}": "%Y%m%d"
}

# 📌 Scan all filenames for matching dates
detected_formats = set()
for filename in os.listdir(folder_path):
    for regex in date_formats:
        if re.search(regex, filename):
            detected_formats.add(date_formats[regex])

# 📌 Display options to the user
print("Detected possible date formats from filenames:")
for i, fmt in enumerate(detected_formats):
    print(f"{i+1}: {fmt}")

# 📌 Let user select format
if not detected_formats:
    print("❌ No date formats detected in filenames.")
    exit()

choice = int(input("Select the correct date format by number: ")) - 1
selected_format = list(detected_formats)[choice]

# 📌 Track skipped files
skipped_files = []

# 📌 Process images
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)

    # Only process image files
    if not filename.lower().endswith(('.jpg', '.jpeg', '.tiff')):
        continue

    # Find date in filename
    match = None
    for regex, fmt in date_formats.items():
        if fmt == selected_format:
            match = re.search(regex, filename)
            if match:
                break

    if not match:
        skipped_files.append(filename)
        continue

    date_str = match.group()
    try:
        date_obj = datetime.strptime(date_str, selected_format)
        exif_date = date_obj.strftime("%Y:%m:%d %H:%M:%S")
    except Exception:
        skipped_files.append(filename)
        continue

    # Load image and EXIF data
    try:
        im = Image.open(file_path)
        exif_dict = piexif.load(im.info.get("exif", b""))

        # Update EXIF DateTime tags
        exif_dict['0th'][piexif.ImageIFD.DateTime] = exif_date.encode()
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = exif_date.encode()
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = exif_date.encode()

        exif_bytes = piexif.dump(exif_dict)
        im.save(file_path, exif=exif_bytes)

        # Also update file modified timestamp
        mod_time = date_obj.timestamp()
        os.utime(file_path, (mod_time, mod_time))

        print(f"✅ Updated: {filename}")

    except Exception as e:
        skipped_files.append(filename)
        continue

# 📌 Report skipped files
if skipped_files:
    print("\n⚠️ Skipped files (no valid date found or error occurred):")
    for f in skipped_files:
        print(f"- {f}")

else:
    print("\n✅ All files processed successfully.")

