import os
import re
from datetime import datetime
import piexif
from PIL import Image
import tkinter as tk
from tkinter import ttk, messagebox

def get_date_formats():
    return [
        r"\d{4}-\d{2}-\d{2}",              # YYYY-MM-DD
        r"\d{2}-\d{2}-\d{4}",              # MM-DD-YYYY
        r"\d{2}_\d{2}_\d{4}",              # MM_DD_YYYY
        r"\d{4}_\d{2}_\d{2}",              # YYYY_MM_DD
        r"\d{4}\d{2}\d{2}",                # YYYYMMDD
        r"\d{2}\d{2}\d{4}"                 # MMDDYYYY
    ]

def parse_date(date_str, date_format):
    try:
        if date_format == r"\d{4}-\d{2}-\d{2}":
            return datetime.strptime(date_str, "%Y-%m-%d")
        elif date_format == r"\d{2}-\d{2}-\d{4}":
            return datetime.strptime(date_str, "%m-%d-%Y")
        elif date_format == r"\d{2}_\d{2}_\d{4}":
            return datetime.strptime(date_str, "%m_%d_%Y")
        elif date_format == r"\d{4}_\d{2}_\d{2}":
            return datetime.strptime(date_str, "%Y_%m_%d")
        elif date_format == r"\d{4}\d{2}\d{2}":
            return datetime.strptime(date_str, "%Y%m%d")
        elif date_format == r"\d{2}\d{2}\d{4}":
            return datetime.strptime(date_str, "%m%d%Y")
    except ValueError:
        return None
    return None

def modify_exif_date(filepath, date):
    try:
        img = Image.open(filepath)
        if img.format not in ['JPEG', 'JPG']:
            return False
        
        exif_dict = piexif.load(img.info.get('exif', b''))
        date_str = date.strftime("%Y:%m:%d %H:%M:%S")
        
        # Update EXIF date fields
        exif_dict['0th'][piexif.ImageIFD.DateTime] = date_str
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = date_str
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = date_str
        
        exif_bytes = piexif.dump(exif_dict)
        img.save(filepath, exif=exif_bytes)
        # Update file modification time
        os.utime(filepath, (date.timestamp(), date.timestamp()))
        return True
    except Exception:
        return False

def process_folder(folder_path, date_format):
    failed_files = []
    
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if not os.path.isfile(filepath):
            continue
            
        # Search for date in filename
        date_match = re.search(date_format, filename)
        if date_match:
            date_str = date_match.group()
            date = parse_date(date_str, date_format)
            if date:
                if not modify_exif_date(filepath, date):
                    failed_files.append(filename)
            else:
                failed_files.append(filename)
        else:
            failed_files.append(filename)
    
    return failed_files

def create_gui(folder_path):
    root = tk.Tk()
    root.title("Select Date Format")
    root.geometry("400x300")
    
    tk.Label(root, text="Select the date format used in image filenames:").pack(pady=10)
    
    date_formats = get_date_formats()
    format_examples = [
        "2023-12-25",
        "12-25-2023",
        "12_25_2023",
        "2023_12_25",
        "20231225",
        "12252023"
    ]
    
    selected_format = tk.StringVar()
    
    for fmt, example in zip(date_formats, format_examples):
        tk.Radiobutton(
            root,
            text=f"Example: {example}",
            variable=selected_format,
            value=fmt
        ).pack(anchor="w", padx=20)
    
    def on_submit():
        if not selected_format.get():
            messagebox.showerror("Error", "Please select a date format")
            return
        
        failed_files = process_folder(folder_path, selected_format.get())
        root.destroy()
        
        if failed_files:
            message = "The following files could not be processed:\n" + "\n".join(failed_files)
            messagebox.showwarning("Processing Complete", message)
        else:
            messagebox.showinfo("Success", "All files processed successfully")
    
    tk.Button(root, text="Submit", command=on_submit).pack(pady=20)
    
    root.mainloop()

def main():
    folder_path = input("Enter the folder path containing images: ")
    if not os.path.isdir(folder_path):
        print("Invalid folder path")
        return
    
    create_gui(folder_path)

if __name__ == "__main__":
    main()