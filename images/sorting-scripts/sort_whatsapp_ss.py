import os
import shutil
from PIL import Image
from tqdm import tqdm

# Define the specific RGB value of green
specific_green = (0, 92, 74)

# Define the source and destination folders
src_folder = os.path.join("krish screenshots")
dst_folder = os.path.join("krish screenshots", "whatsapp")

# Create the destination folder if it doesn't exist
if not os.path.exists(dst_folder):
    os.makedirs(dst_folder)

# Get a list of all the files in the screenshots folder
files = os.listdir(src_folder)

# For each file in the folder
for file in tqdm(files, desc="Processing images", unit="image"):
    # Open the image
    img = Image.open(os.path.join(src_folder, file))

    # Check each pixel
    for pixel in img.getdata():
        if pixel == specific_green:
            # If the pixel's RGB value matches the specific green, move the file to the different folder
            shutil.move(os.path.join(src_folder, file), os.path.join(dst_folder, file))
            break
