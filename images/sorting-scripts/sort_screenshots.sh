#!/bin/bash

# Path to the folder containing the screenshots
screenshots_folder="/home/krishnaraj/Pictures/Screenshots"

# Go to the screenshots folder
cd "$screenshots_folder" || exit

# Loop through all the screenshots in the folder
for screenshot in *.png *.jpg *.jpeg *.gif *.bmp *.tiff; do
  if [ -f "$screenshot" ]; then
    # Get the year and month from the screenshot's creation timestamp
    year=$(date -r "$screenshot" +%Y)
    month=$(date -r "$screenshot" +%m)
    
    # Create the year folder if it doesn't exist
    if [ ! -d "$year" ]; then
      mkdir "$year"
    fi
    
    # Create the month subfolder if it doesn't exist
    if [ ! -d "$year/$year-$month" ]; then
      mkdir "$year/$year-$month"
    fi
    
    # Move the screenshot to the appropriate folder
    mv "$screenshot" "$year/$year-$month"
  fi
done