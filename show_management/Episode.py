import os

class Episode:
    """
    A class to represent an episode of a show
    """
    description = ''
    directory = None
    season = 0
    number = 0
    show = ''
    raw_filename = None
    raw_cleaned_filename = None
    supposed_filename = None
    extension = None

    @property
    def final_filename(self):
        """
            Removes all special characters from the filename keeping only letters, numbers and spaces. Changes hyphens to spaces. Then prepends the show name and season number to the filename.
        """
        if not self.supposed_filename:
            return ''
        return self.show + ' ' +  self.season_and_number + ' ' + self.supposed_filename.title() + '.' + self.extension

    @property
    def fixed_filepath(self):
        return os.path.join(self.directory, self.final_filename)
    
    @property
    def raw_filepath(self):
        return os.path.join(self.directory, self.raw_filename)
    
    @property
    def season_and_number(self):
        return 'S' + str(self.season).zfill(2) + 'E' + str(self.number).zfill(4)