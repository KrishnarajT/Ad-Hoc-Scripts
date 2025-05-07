#!/bin/bash

# Prompt user for the directory
read -p "Enter the full path to the directory: " dir

# Check if directory exists
if [ ! -d "$dir" ]; then
    echo "The specified directory does not exist. Exiting."
    exit 1
fi

# Prompt for original extension (without dot)
read -p "Enter the extension to change from (without dot, e.g., mp4): " ext_from

# Prompt for new extension (without dot)
read -p "Enter the extension to change to (without dot, e.g., mp3): " ext_to

# Find and rename files
find "$dir" -type f -name "*.${ext_from}" | while read file; do
    base="${file%.*}"
    mv "$file" "${base}.${ext_to}"
    echo "Renamed: $(basename "$file") -> $(basename "${base}.${ext_to}")"
done

echo "All .${ext_from} files in $dir and its subdirectories have been renamed to .${ext_to}."
