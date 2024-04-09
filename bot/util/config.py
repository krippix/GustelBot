# default
import logging
import os
from pathlib import Path
# pip
# internal


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
        "sounds_custom": Path
    }
    # configuration options and their default
    options = {
        "GUSTELBOT_LOGLEVEL": "info",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "gustelbot",
        "POSTGRES_USER": "gustelbot",
        "POSTGRES_PASSWORD": "password",
        "DISCORD_TOKEN": "xxxxx",
        "DISCORD_DEBUG_GUILDS": ""
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # folders
        self.folders["root"] = Path(__file__).parent.parent.parent
        self.folders["data"] = Path(self.folders["root"]).joinpath("data")
        self.folders["sounds"] = Path(self.folders["data"]).joinpath("sounds")
        # default folder cannot be played from /play command
        self.folders["sounds_default"] = Path(self.folders["sounds"]).joinpath("default")
        self.folders["sounds_custom"] = Path(self.folders["sounds"]).joinpath("custom")

        self.ensureBaseFolders()

        self.checkConfig()

    def checkConfig(self):
        """Checks if needed environment variables were set
        """
        # check for each key if set at all
        for key in self.options.keys():
            if os.environ.get(key) is None:
                logging.warning(f"Variable {key} not provided, defaulting to {self.options[key]}")
                os.environ[key] = self.options[key]

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

    def get_debug_guilds(self) -> list[str]:
        result = os.environ["DISCORD_DEBUG_GUILDS"].split(",")
        if result == [""]:
            return ""
        return result

    def get_loglevel(self) -> int:
        """Returns configured loglevel as integer, defaults to info
        """
        loglevel_input = os.environ.get("GUSTELBOT_LOGLEVEL").lower()

        loglevels = {"debug": 10, "info": 20, "warning": 30, "error": 40, "critical": 50}

        try:
            return loglevels[loglevel_input]
        except Exception:
            logging.error("Failed to determine loglevel, defaulting to INFO.")
            return 20

    def get_database_config(self) -> dict:
        """Returns postgres config string
        {host,port,db,user,password}
        """
        return {
            "host": os.environ.get("POSTGRES_HOST"),
            "port": os.environ.get("POSTGRES_PORT"),
            "db": os.environ.get("POSTGRES_DB"),
            "user": os.environ.get("POSTGRES_USER"),
            "password": os.environ.get("POSTGRES_PASSWORD")
        }

    def get_discord_token(self) -> str:
        """Returns discord token
        """
        return os.environ.get("DISCORD_TOKEN")
