import configparser
import os
from pathlib import Path
from pathlib import Path

class Config:

    def __init__(self, filename='config.ini'):
        self.filename = filename
        self.config = configparser.ConfigParser()
        self.load()
    
    def load(self):
        if os.path.exists(self.filename):
            self.config.read(self.filename)
        else:
            self.create_default_config()
    
    def create_default_config(self):
        desktop_path = str(Path.home() / 'Desktop')
        self.config['FOLDER_PATH'] = {
            'folder_path1': desktop_path,
            'folder_path2': desktop_path,
            'folder_path3': desktop_path
        }
        self.config['REPEAT_MUSIC'] = {
            'repeat_track': 'False',
            'repeat_list': 'True',
            'all_list': 'True'
        }
        self.save()
    
    def get(self, section, option):
        try:
            return self.config[section][option]
        except KeyError as e:
            raise KeyError(f"Missing section or option in config: {e}")
    
    def set(self, section, option, value):
        self.config[section][option] = value
    
    def save(self):
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)
