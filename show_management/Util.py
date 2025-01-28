from fuzzywuzzy import fuzz
from show_management.Episode import Episode
import re

class Util:
    def get_episode_number(name_with_number):
        """Returns the episode number from the episode name with formats number.name (no ext)"""
        return int(name_with_number.split('.')[0])

    def get_episode_name(name_with_ext):
        """Returns the episode name for formats where you have number.name (no ext)"""
        return name_with_ext.split('.', maxsplit=1)[1].strip()
    
    def get_episode_extension(name_with_ext):
        """Returns the file extension from a filename."""
        return name_with_ext.split('.')[-1].strip()

    def get_name_without_extension(name_with_ext):
        """Returns the episode name without the file extension."""
        name_without_extension = name_with_ext.split('.')[:-1]
        return ''.join(name_without_extension)

    def fuzzy_match(original_episodes: list[Episode], episode_name: str, ratio: int):
        """
        Finds the best match for the given episode name among the original episodes.

        Args:
        - original_episodes (list): A list of Episode objects.
        - episode_name (str): The name to search for.
        - ratio (int): The minimum fuzziness ratio.

        Returns:
        - The matching Episode object or a new Episode object if no match is found.
        """

        best_match = None
        best_ratio = 0

        for episode in original_episodes:
            current_ratio = fuzz.ratio(episode.supposed_filename, episode_name)
            # if 'police takes husband in custody' in episode_name:
            #     print(f'Ratio: {current_ratio} - {episode.supposed_filename} - {episode_name}')
            if current_ratio > best_ratio and current_ratio >= ratio and episode.raw_cleaned_filename is None:
                best_ratio = current_ratio
                best_match = episode

        if best_match:
        
            best_match.raw_cleaned_filename = episode_name
        return best_match or Episode()

    def clean_name(name):
        """Cleans the episode name by removing special characters. Replaces hyphens by spaces"""
        # replace hyphens with spaces
        name = re.sub('[-]', '', name)
        # remove all special characters
        name = re.sub('[^a-zA-Z0-9\s]', '', name)
        # remove leading and trailing whitespaces
        name = name.strip()
        # lowercase the string
        name = name.lower()
        return name