import logging
import os
import configparser
from pathlib import Path

class Config:
    '''
    This will handle configuration in this project.
    config.ini is supposed to be generated and repaired in this class in case anything is missing.
    Please use get_config() if you only need the string in the ini
    '''
    # required folders should be written here in order to automatically create them
    folders = {
        "root": Path,
        "data": Path,
        "sounds": Path,
        "sounds_default": Path,
        "sounds_custom" : Path
    }

    config: configparser.ConfigParser()
    
    def __init__(self):
        # folders
        self.folders["root"]           = Path(__file__).parent.parent.parent
        self.folders["data"]           = Path(self.folders["root"]).joinpath("data")
        self.folders["sounds"]         = Path(self.folders["data"]).joinpath("sounds")
        self.folders["sounds_default"] = Path(self.folders["sounds"]).joinpath("default") # Hardcoded folders, cannot be played with /play command
        self.folders["sounds_custom"]  = Path(self.folders["sounds"]).joinpath("custom")
        
        # files
        self.INI_FILE = Path(self.folders["data"]).joinpath("config.ini")
        self.DATABASE = Path(self.folders["data"]).joinpath("database.db")

        self.config = configparser.ConfigParser()
        self.ensureBaseFolders()

        self.checkConfig()
    

    def generateConfig(self):
        '''Generates entire configuration anew, this will CLEAR any previous configuration'''
        self.config = self.get_default_config()

        self.writeConfig()
        
        logging.info("Success! config.ini has been created!")
        logging.info("Change its parameters and restart the program.")
        exit()


    def checkConfig(self):
        '''Check if config.ini is present, and whether it's incomplete. Repairs missing parts.'''

        # Check if 'config.ini' is present
        if not os.path.exists(self.INI_FILE):
            logging.warning("ini file doesen't exist, creating...")
            self.generateConfig()

        # Check if 'config.ini' is missing sections or keys
        defaultconfig = self.get_default_config()
        self.config.read(self.INI_FILE)

        # Adding missing sections/keys (Using defaultconfig as basefile)
        for section in defaultconfig.sections():
            # Adding sections
            if not section in self.config.sections():
                logging.warning(f"Section '{section}' missing. Adding it now.")
                self.config.add_section(section)
            
            # Adding keys to sections
            for defaultkey in defaultconfig.items(section):
                currentKeys = []

                # Create list of current section keys
                for key in self.config.items(section):
                    currentKeys.append(key[0])

                if not defaultkey[0] in currentKeys:
                    logging.warning(f"Key '{defaultkey[0]}' missing. Adding it now.")
                    self.config[section][defaultkey[0]] = defaultkey[1]
                
        self.writeConfig()
        logging.info("Config check completed.")


    def writeConfig(self):
        '''Write config to file'''
        try:
            with open(self.INI_FILE, 'w') as configfile:
                self.config.write(configfile)
        except Exception as e:
            logging.error(f"Failed to write 'config.ini': {e}")
            exit()

    def ensureBaseFolders(self):
        '''Creates all folders listed '''
        for folder in self.folders.values():
            self.ensureFolder(folder)

    @staticmethod
    def ensureFolder(folder_path: Path):
        '''takes path, and creates missing folders in that path if they don't exist'''
        
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path)
            except Exception as e:
                logging.error(f"Failed to create directories for {folder_path}: {e}")

    #
    # ------ GETTER ------
    #

    def get_default_config(self):
        '''Returns previously defined default config'''
        # This is where you can define what the config.ini is supposed to look like
        # DO NOT SET ANY API KEYS OR PASSWORDS AS DEFAULT
        defaultconfig = configparser.ConfigParser()

        defaultconfig['AUTH'] = {
            "discord_token" : ""
        }

        defaultconfig['CLIENT'] = {
            "prefix" : "!",
            "debug_guild" : ""
        }

        defaultconfig['SCRIPT'] = {
            "loglevel" : "info"
        }

        return defaultconfig

    def get_config(self, category, key):
        '''Calling just the string within the .ini without any checks'''
        
        try:
            return self.config[category][key]
        except Exception as e:
            logging.error(f"Failed to read 'config.ini': {e}")

    def get_inipath(self) -> Path:
        return self.INI_FILE


    def get_logpath(self) -> Path:
        pass


    def get_loglevel(self) -> int:
        '''Returns integer value of string in the config. Defaults to info'''
        loglevel_input = self.get_config("SCRIPT","loglevel").lower()

        loglevels = {"debug": 10, "info": 20, "warning": 30, "error": 40, "critical": 50}
            
        if loglevel_input in loglevels:
            return loglevels[loglevel_input]
        
        logging.error("Failed to determine loglevel, defaulting to debug.")
        return 20


    def get_bot_prefix(self):
        '''Attempts to get bot prefix from config.ini. Defaults to "!".'''
        prefix = self.get_config("CLIENT","prefix")

        if prefix == "":
            logging.error("No Prefix configured, defaulted to '!'")
            prefix = "!"
        
        return prefix

    #
    # ------ SETTER ------
    #

    def set_config(self, category, key, value):
        ''''Sets config option.'''
        self.config[category][key] = value
        self.writeConfig()
