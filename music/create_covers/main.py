import os
import random
from PIL import Image
from pathlib import Path

# Function to crop image to square (center crop)
def crop_to_square(image):
    width, height = image.size
    size = min(width, height)
    
    left = (width - size) // 2
    top = (height - size) // 2
    right = (width + size) // 2
    bottom = (height + size) // 2

    return image.crop((left, top, right, bottom))

# Function to create a cover.jpg for each subfolder
def create_cover_image_for_folders(base_dir, images_folder):
    # Get list of images from the specified folder
    images = [f for f in Path(images_folder).iterdir() if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}]

    if not images:
        print("No images found in the provided folder.")
        return

    # Iterate through each subfolder in the base directory
    for subfolder in Path(base_dir).iterdir():
        if subfolder.is_dir():
            print(f"Creating cover for: {subfolder}")
            
            # Choose a random image
            image_path = random.choice(images)
            images.remove(image_path)  # Remove the chosen image so it isn't repeated

            # Open and crop the image
            img = Image.open(image_path)
            img_cropped = crop_to_square(img)

            # Save the image as 'cover.jpg' in the subfolder
            cover_path = subfolder / 'cover.jpg'
            img_cropped.save(cover_path)
            print(f"Cover image saved at: {cover_path}")

# Main function to input folder and execute
if __name__ == "__main__":
    base_directory = input("Enter the base folder path: ").strip()
    images_folder = input("Enter the folder path containing images: ").strip()
    
    if os.path.isdir(base_directory) and os.path.isdir(images_folder):
        create_cover_image_for_folders(base_directory, images_folder)
    else:
        print("The provided paths are not valid.")
