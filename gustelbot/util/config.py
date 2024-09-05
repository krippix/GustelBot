# default
import logging
import os
from pathlib import Path
# pip
# internal


class Config:
    """
    This will handle configuration in this project.
    config.ini is supposed to be generated and repaired in this class in case anything is missing.
    Please use get_config() if you only need the string in the ini
    """
    # required folders should be written here in order to automatically create them
    folders = {
        "root": Path(),
        "data": Path(),
        "sounds": Path(),
        "sounds_default": Path(),
        "sounds_custom": Path()
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

        for folder in self.folders.values():
            Config.ensure_folder(folder)

        self.check_config()

    def check_config(self):
        """
        Checks if needed environment variables were set
        """
        # check for each key if set at all
        for key in self.options.keys():
            if os.environ.get(key) is None:
                logging.warning(f"Variable {key} not provided, defaulting to {self.options[key]}")
                os.environ[key] = self.options[key]

    @staticmethod
    def is_superuser(user_id: int):
        if (super_user := os.environ.get("GUSTELBOT_SUPERUSER")) is None:
            return False
        return int(super_user) == user_id

    @staticmethod
    def ensure_folder(folder_path: Path):
        """
        Takes Path to a folder and creates it if it doesn't exist
        """
        if folder_path.exists():
            return
        os.makedirs(folder_path)

    #
    # ------ GETTER ------
    #

    @staticmethod
    def get_debug_guilds() -> list[str]:
        result = os.environ["DISCORD_DEBUG_GUILDS"].split(",")
        return result

    @staticmethod
    def get_loglevel() -> int:
        """Returns configured loglevel as integer, defaults to info
        """
        loglevel_input = os.environ.get("GUSTELBOT_LOGLEVEL").lower()

        log_levels = {"debug": 10, "info": 20, "warning": 30, "error": 40, "critical": 50}

        return log_levels.get(loglevel_input, 20)

    @staticmethod
    def get_database_config() -> dict:
        """
        Returns postgres config string
        {host,port,db,user,password}
        """
        return {
            "host": os.environ.get("POSTGRES_HOST"),
            "port": os.environ.get("POSTGRES_PORT"),
            "db": os.environ.get("POSTGRES_DB"),
            "user": os.environ.get("POSTGRES_USER"),
            "password": os.environ.get("POSTGRES_PASSWORD")
        }

    @staticmethod
    def get_discord_token() -> str:
        """Returns discord token
        """
        return os.environ.get("DISCORD_TOKEN")
