# external
import psycopg2
from psycopg2 import extensions
# python native
import logging, os, time
from pathlib import Path
# project
from util import config


class Database():
    """Implements a connection to a postgres db.
    Using 'with' on each connection usage ensures that they are commited after finishing.
    """

    connection: extensions.connection
    cursor: extensions.cursor

    def __init__(self):
        self.logger   = logging.getLogger(__name__)
        self.settings = config.Config()
        self.__connect()
        self.check()

    # ---- public functions

    def check(self):
        self.__ensure_tables()
        # TODO same for columns?
    
    # -- get/set/add/delete ----

    def get_user(self, id: str, server_id="") -> dict | None:
        """Returns user with the provided id

        Args:
            id: user's discord id
            server_id: context discord server if empty returns username

        Returns:
            json: {id,name}
        """
        with self.connection as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id,name FROM discord_users WHERE user_id=%s;",(id,))
                result = cur.fetchone()
        
        if result is None:
            return None
        if server_id == "":
            return {"id": result[0], "name": result[1]}
        
        # get server's display name
        with self.connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT displayname FROM discord_user_displaynames "+
                    "WHERE user_id=%(userid)s AND server_id=%(serverid)s;",
                    {'userid' : id, 'serverid' : server_id}
                )
                displayname = cur.fetchone()
        # if no name found fall back to username
        if displayname is None:
            return {"id": result[0], "name": result[1]}
        return {'id': result[0], 'name': displayname}
    
    def add_user(self, id: int, name: str):
        """Add a user to the database

        Args:
            id: discord user id
            name: discord username
            server: server id where user is beeing added from
            displayname: servers displayname
        """
        with self.connection as conn:
            # add user to db
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO discord_users (user_id,name) VALUES (%(id)s,%(name)s) "+
                    "ON CONFLICT (user_id) DO UPDATE "+
                    "SET name=%(name)s;"
                    ,{'id' : id, 'name' : name}
                )
        return

    def delete_user(self, id):
        pass
        # TODO


    def add_user_displayname(self, user_id: int, server_id: int, name: str):
        """Adds user display name to the database

        Args:
            user_id: user's discord id
            server_id: discord server id where displayname is used
            name: the displayname
        """
        with self.connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO discord_user_displaynames (user_id,server_id,displayname) "+
                    "VALUES (%(user_id)s,%(server_id)s,%(displayname)s) "+
                    "ON CONFLICT (user_id,server_id) DO UPDATE "+
                    "SET displayname=%(displayname)s",
                    {'user_id' : user_id, 'server_id' : server_id, 'displayname' : name}
                )
        return
        
    def add_server(self, id: int, name="unknown"):
        """Adds discord server to database

        Args:
            id: discord server id
            name: server displayname. Defaults to "unknown".
        """
        with self.connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO discord_servers (server_id,servername) "+
                    "VALUES (%(id)s,%(name)s) "+
                    "ON CONFLICT (server_id) DO UPDATE "+
                    "SET servername=%(name)s;",
                    {'id' : id, 'name' : name}
                )
        return


    def get_brotato_char(self, char="") -> list[dict] | None:
        """Returns single char if string provided, all if not
        Args:
            char: brotato char display name
        Returns:
            dict: {id, name_en, name_de}
        """
        result_list = []

        # no input given
        if char == "":
            with self.connection as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT char_id,name_en,name_de FROM brotato_chars;")
                    dbresult = cur.fetchall()
            for tuple in dbresult:
                result_list.append({'id' : tuple[0], 'name_en' : tuple[1], 'name_de' : tuple[2] })
            if len(result_list) == 0:
                return None
            return result_list
        
        # input given
        with self.connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT char_id,name_en,name_de FROM brotato_chars "+
                    "WHERE LOWER(name_de) = LOWER(%(name)s) OR "+
                    "LOWER(name_en) = LOWER(%(name)s);",
                    {'name' : char}
                )
                dbresult = cur.fetchone()
        if dbresult is None:
            return None
        return [{'id' : dbresult[0], 'name_en' : dbresult[1], 'name_de' : dbresult[2] }]

    def add_brotato_char(self, char: str):
        """Adds new character to database

        Args:
            char: name of the character
        """
        if self.get_brotato_char(char) is not None:
            return
        with self.connection as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO brotato_chars (name_de) VALUES (%(name)s);",{'name' : char})
        return

    def get_brotato_highscore(self, diff: int, character: str | None, guild_id: int) -> tuple[list[tuple],list]:
        """Get highscores from database

        Args:
            diff: difficulty

        Returns:
            tuple[list[tuple],list]: ([(highscore,...),(highscore,...)],[heading1,heading2,...])
        """
        # handle if char is set/not set
        if character is not None:
            char_id = self.get_brotato_char(character)
            if char_id is not None:
                char_id = char_id[0]['id']
        else:
            char_id = None

        # this ist horrible, but sql commands with strings as parameters scare me
        if diff is None:
            if char_id is None:
                # diff: no, char, no
                with self.connection as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT du.name,br.wave,br.danger,bc.name_de FROM brotato_runs br "+
                            "INNER JOIN discord_users du ON du.user_id = br.user_id "+
                            "INNER JOIN brotato_chars bc ON bc.char_id = br.char_id "+
                            "WHERE br.server_id=%(server_id)s "+
                            "ORDER BY wave DESC "+
                            "LIMIT 20;",
                            { 'server_id' : guild_id }
                        )
                        result = cur.fetchall()
                        heading = ["Spieler", "Welle", "Gefahr", "Charakter"]
            else:
                # diff: no, char yes
                with self.connection as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT du.name,br.wave,br.danger FROM brotato_runs br "+
                            "INNER JOIN discord_users du ON du.user_id = br.user_id "+
                            "INNER JOIN brotato_chars bc ON bc.char_id = br.char_id "+
                            "WHERE br.char_id=%(char_id)s "+
                            "AND br.server_id=%(server_id)s "+
                            "ORDER BY wave DESC "+
                            "LIMIT 20;",
                            { 'char_id' : char_id, 'server_id' : guild_id },
                        )
                        result = cur.fetchall()
                        heading = ["Spieler", "Welle", "Gefahr"]
        else:
            if char_id is None:
                # diff: yes, char, no
                with self.connection as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT du.name,br.wave,bc.name_de FROM brotato_runs br "+
                            "INNER JOIN discord_users du ON du.user_id = br.user_id "+
                            "INNER JOIN brotato_chars bc ON bc.char_id = br.char_id "+
                            "WHERE br.danger=%(danger)s "+
                            "AND br.server_id=%(server_id)s "+
                            "ORDER BY wave DESC "+
                            "LIMIT 20;",
                            { 'danger' : diff, 'server_id' : guild_id }
                        )
                        result = cur.fetchall()
                        heading = ["Spieler", "Welle", "Charakter"]
            else:
                with self.connection as conn:
                    # diff: yes, char, yes
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT du.name,br.wave FROM brotato_runs br "+
                            "INNER JOIN discord_users du ON du.user_id = br.user_id "+
                            "INNER JOIN brotato_chars bc ON bc.char_id = br.char_id "+
                            "WHERE br.danger=%(diff)s "+
                            "AND br.char_id=%(char_id)s "+
                            "AND br.server_id=%(server_id)s "+
                            "ORDER BY wave DESC "+
                            "LIMIT 20;",
                            { "diff" : diff, "char_id" : char_id, 'server_id' : guild_id }
                        )
                        result = cur.fetchall()
                        heading = ["Spieler", "Welle"]
        if result is None:
            return None
        return (result,heading)

    def add_brotato_run(self, char: str, wave: int, danger: int, user_id: str, server_id: int):
        """Creates new brotato run in the database

        Args:
            char: _description_
            wave: _description_
            danger: _description_
            user_id: _description_
            server_id: _description_
        """
        char_id = self.get_brotato_char(char)[0]['id']

        with self.connection as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO brotato_runs (user_id,server_id,char_id,wave,danger,timestamp) "+
                    "VALUES (%(user_id)s,%(server_id)s,%(char_id)s,%(wave)s,%(danger)s,%(timestamp)s);",
                    {
                        'user_id' : user_id,
                        'server_id' : server_id,
                        'char_id' : char_id,
                        'wave' : wave,
                        'danger' : danger,
                        'timestamp' : int(time.time())
                    }
                )

    # -- private functions

    def __ensure_tables(self):
        """Executes all sql files provided in data/schemas, starting with base.sql
        """
        schema_folder = self.settings.folders["data"].joinpath("schemas")

        # create base schema
        with self.connection as conn:
            with conn.cursor() as cur:
                cur.execute(open(schema_folder.joinpath("base.sql"), "r").read())

        # create all other schemas
        schemas = [x for x in os.listdir(schema_folder) if x != "base.sql" and x.endswith(".sql")]

        for schema in schemas:
            current_path = schema_folder.joinpath(schema)
            with self.connection as conn:
                with conn.cursor() as cur:
                    cur.execute(open(current_path, "r").read())
        return

    def __connect(self):
        """Connect to postgres database
        """
        ps_login = {
            'database' : self.settings.get_config("POSTGRES","database"),
            'user'     : self.settings.get_config("POSTGRES","user"),
            'password' : self.settings.get_config("POSTGRES","password"),
            'host'     : self.settings.get_config("POSTGRES","host"),
            'port'     : self.settings.get_config("POSTGRES","port")
        }
        settings_provided = True
        for x in ps_login.keys():
            if ps_login[x] == "":
                self.logger.error(f"'{x}' was not set in config.ini")
                settings_provided = False
        
        if not settings_provided:
            raise Exception("Database Unavailable due to missing credentials, port or hostname.")
        
        self.connection = psycopg2.connect(
            database = ps_login['database'],
            user     = ps_login['user'],
            password = ps_login['password'],
            host     = ps_login['host'],
            port     = ps_login['port']
        )

if __name__ == "__main__":
    logging.error("This file is not supposed to be executed.")
    exit()