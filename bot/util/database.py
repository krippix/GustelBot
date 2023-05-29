# external
import sqlite3
# python native
import logging, os, time, json
from pathlib import Path
# project
from util import config


class Database():
    """Implements sqlite3 database"""

    connection: sqlite3.Connection
    cursor: sqlite3.Cursor

    def __init__(self):
        self.logger     = logging.getLogger(__name__)
        self.settings   = config.Config()
        self.connection = sqlite3.connect(self.settings.DATABASE)
        self.cursor     = self.connection.cursor()
        self.check()

    # -- database basics --

    def check(self):
        """Checks if the database contains all required tables. Attempts to fix any problems."""
        default_structure = Database.json_to_dict(self.settings.folders["data"].joinpath("sqlite3_config.json"))
        for table in default_structure:
            if not self.table_exists(table):
                self.logger.error(f"Table {table} is missing. Creating replacement...")
                self.cursor.execute(default_structure[table])
        self.connection.commit()

    def table_exists(self, table: str) -> bool:
        """Checks if provided table exists."""
        result = self.cursor.execute("SELECT name FROM sqlite_schema WHERE type ='table' AND name = ?;", (table,)).fetchall()

        if len(result) == 0:
            return False
        if len(result) == 1:
            return True
        self.logger.critical("Table appears to exist multiple times. Database may be inconsistent.")

    # ---- Getter Functions ----

    def get_user(self, id: str) -> dict | None:
        """Returns user object with given id."""
        db_result = self.cursor.execute("SELECT id_pk,displayname FROM users WHERE id_pk=?",(id,)).fetchall()

        if len(db_result) != 1:
            return None
        
        db_result = db_result[0]

        return {"id": db_result[0], "displayname": db_result[1]}
    
    def get_brotato_char(self, char: str) -> dict | None:
        """Returns brotato char information by string provided
        Args:
            char: brotato char display name
        Returns:
            dict: {id, name_en, name_de}
        """
        db_result = self.cursor.execute(
            "SELECT id_pk,name_en,name_de FROM brotato_chars WHERE UPPER(name_de)=UPPER(?) OR UPPER(name_de)=UPPER(?)",
            (char,char)
        ).fetchall()

        if len(db_result) != 1:
            return None
        
        db_result = db_result[0]

        return {"id": db_result[0], "name_en": db_result[1], "name_de": db_result[2]}

    def get_brotato_char_all(self) -> list:
        """Returns all brotato chars (german names)
        Returns:
            list of strings
        """
        db_result = self.cursor.execute("SELECT name_de FROM brotato_chars").fetchall()
        result_list = []

        for tpl in db_result:
            result_list.append(tpl[0])

        return result_list

    # ---- Setter Functions ----

    # ---- Other Functions ----
    
    # -- add --
    
    def add_user(self, id: int, displayname: str):
        """Adds Discord user to the database

        Args:
            id: discord user-id
            displayname: discord user displayname
        """
        self.cursor.execute("INSERT INTO users (id_pk,displayname) VALUES (?,?)",(id,displayname))
        self.connection.commit()

    def add_brotato_char(self, char: str):
        #TODO: remove at some point and provide full database
        self.cursor.execute("INSERT INTO brotato_chars (name_de) VALUES (?)",(char,))
        self.connection.commit()

    def add_brotato_run(self, char: str, wave: int, danger: int, user_id: str, discord_id: int):
        """_summary_

        Args:
            char: Character used
            round: wave reached
            danger: danger level selected
            user_id: id of user who did the run
        """
        char_dict = self.get_brotato_char(char)

        if char_dict is None:
            self.add_brotato_char(char)
            char_dict = self.get_brotato_char(char)

        self.cursor.execute(
            "INSERT INTO brotato_runs (char_id_fk,wave,danger,timestamp,users_id_fk,discord_id)"+
            "VALUES (?,?,?,?,?,?)",
            (char_dict["id"],wave,danger,int(time.time()),user_id,discord_id)
            )
        self.connection.commit()

    # -- update --

    # -- helper functions --
    @staticmethod
    def json_to_dict(file: Path) -> dict:
        """Returns provided .json file as dictionary

        Args:
            file: Path to file

        Returns:
            _description_
        """
        with open(file) as json_file:
            data = json.load(json_file)
        return data


if __name__ == "__main__":
    logging.error("This file is not supposed to be executed.")
    exit()