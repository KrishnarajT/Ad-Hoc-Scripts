import sys
import os
import pathlib

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)
from show_management.Episode import Episode
from show_management.Util import Util

# list of original episodes
original_episodes = []
with open("shows/fir/fir_episode_names.txt") as f:
    for line in f:
        current_episode = Episode()
        current_episode.show = 'FIR'
        current_episode.season = 1
        current_episode.number =  Util.get_episode_number(line)
        current_episode.supposed_filename = Util.clean_name(Util.get_episode_name(line))
        current_episode.extension = Util.get_episode_extension(line)
        original_episodes.append(current_episode)

# list of episodes from the directory we gotta fix
show_path = r"\\KRISH-HOME-NAS\shared\mnt\media\Classic Shows\FIR"

filenames = [i for i in os.listdir(show_path) if os.path.isfile(os.path.join(show_path, i))]
filenames = [filename for filename in filenames if filename[-3:] == "mkv" or filename[-3:] == "mp4"]

print("Found %d files in the directory, corresponding with %d original episodes" %(len(filenames), len(original_episodes)))

tofix_episodes = []
for filename in filenames:
    current_episode  = Episode()
    current_episode.show = 'FIR'
    current_episode.season = 1
    current_episode.raw_filename = filename
    current_episode.raw_cleaned_filename = Util.clean_name(Util.get_name_without_extension(filename))
    current_episode.directory = show_path

    # fuzzy match with all the episodes in original list
    supposed_episode = Util.fuzzy_match(original_episodes, current_episode.raw_cleaned_filename, 80)
    current_episode.supposed_filename = supposed_episode.supposed_filename
    current_episode.number = supposed_episode.number
    current_episode.extension = Util.get_episode_extension(filename)

    tofix_episodes.append(current_episode)

# now we have them all sorted


# output
# what episodes you need to download
# if unaltered filename is none in the original episodes list, its not downloaded

print("Here are the episodes that you need to download:")

not_found_count = 0
for episode in original_episodes:
    if episode.raw_cleaned_filename == None:
        print(episode.supposed_filename + " - " + str(episode.number))
        not_found_count += 1

print("Found %d unaltered filenames that are not in the original list." %(not_found_count))


not_found_supposed = []
for episode in tofix_episodes:
    if episode.supposed_filename == None or episode.number is None:
        print(episode.raw_cleaned_filename + "  -  " + str(episode.number))
        not_found_supposed.append(episode)
    else:
        print(episode.directory + episode.final_filename)
        pathlib.Path(episode.raw_filepath).rename(episode.fixed_filepath)

print("Found %d unaltered filenames that are not in the original list. Should be 0" %(len(not_found_supposed)))

## to do find duplicates in the original episode names, and then download them. 