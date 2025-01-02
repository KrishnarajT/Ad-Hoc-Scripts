import os
import shutil
from tqdm import tqdm
import face_recognition
import logging
import traceback

# Path to the folder containing the images
images_folder = "./pics"

# Output folders for images with faces and extras
output_folder_faces = "faces"
output_folder_extras = "extras"

# Create output folders if they don't exist
os.makedirs(output_folder_faces, exist_ok=True)
os.makedirs(output_folder_extras, exist_ok=True)

# Function to check if an image contains a face
def contains_face(image_path):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    return len(face_locations) > 0

# Get the list of image files in the folder
image_files = [image_file for image_file in os.listdir(images_folder) if os.path.isfile(os.path.join(images_folder, image_file))]

# Initialize the progress bar
progress_bar = tqdm(total=len(image_files), desc="Processing Images", unit="image")

# Loop through all the images in the folder
for image_file in image_files:
    try:
        image_path = os.path.join(images_folder, image_file)
        if contains_face(image_path):
            # Move image to the folder for images with faces
            shutil.move(image_path, os.path.join(output_folder_faces, image_file))
        else:
            # Move image to the folder for extras
            shutil.move(image_path, os.path.join(output_folder_extras, image_file))

    # Update the progress bar and status message

    except Exception as err: 
        print("Error occured here: ", err)
        print("Output from the Traceback module")
        traceback.print_exc()
        print("Output from the logging module")
        logging.exception("Error occured here: ", err)
    progress_bar.update(1)

# Close the progress bar
progress_bar.close()

print("Face detection and sorting completed!")
