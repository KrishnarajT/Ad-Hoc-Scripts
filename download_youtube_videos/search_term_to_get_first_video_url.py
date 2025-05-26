from yt_dlp import YoutubeDL
# include progress bar for number of search terms in the file, and print the progress as it goes through each term.
import tqdm

def get_first_youtube_link(query):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': 'in_playlist',
        'default_search': 'ytsearch1',  # only get first result
    }

    with YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(query, download=False)
        if 'entries' in result and result['entries']:
            return result['entries'][0]['url']
        return None

def process_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    updated_lines = []
    for _, line in enumerate(lines):
        line = line.strip()
        if not line:
            updated_lines.append('\n')
            continue
        updated_lines.append(line + '\n')
        link = get_first_youtube_link(line)
        # Use tqdm to show progress bar
        tqdm.tqdm.write(f"Processing: {line}")
        tqdm.tqdm.write(f"Found link: {link if link else 'No result found.'}")
        # Append the link or a message if no link was found
        tqdm.tqdm.write(f"Progress: {_}/{len(lines)}")
        
        if link:
            updated_lines.append(f"{link}\n")
        else:
            updated_lines.append("No result found.\n")
    tqdm.tqdm.write("Processing complete. Writing results to file...")
    # Write the updated lines back to the file
    with open(filepath, 'w') as f:
        f.writelines(updated_lines)
    tqdm.tqdm.write("Results written to file successfully.")

    # write a file that has only links
    links_only = [line for line in updated_lines if line.startswith('http')]
    
    with open('links_only.txt', 'w') as f:
        f.writelines(links_only)

# ask user for path, make sure it exists. 

print("Enter the path to your text file containing search terms")
path = input().strip()
import os
if os.path.exists(path) and os.path.isfile(path):
    process_file(path)
    
else:
    print("File does not exist or is not a valid file. Please check the path and try again.")
    exit(1)