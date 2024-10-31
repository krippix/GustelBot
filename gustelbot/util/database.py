# default
import logging
import os
import time
import discord
# pip
import psycopg2
from psycopg2 import extensions
from psycopg2.extensions import connection
# internal
from . import config
from . import dataclasses


class Database:
    """
    Implements a connection to a postgres db.
    Using 'with' on each connection usage ensures that they are commited after finishing.
    """
    # ---- generic functions, multiple modules
    @staticmethod
    def new_connection() -> connection:
        """Connect to postgres database
        """
        login = config.Config().get_database_config()

        return psycopg2.connect(
            database=login['db'],
            user=login['user'],
            password=login['password'],
            host=login['host'],
            port=login['port']
        )

    @staticmethod
    def check(conn: connection):
        Database.__ensure_tables(conn)

    # -- get/set/add/delete ----

    @staticmethod
    def get_server(conn: connection, server_id=None) -> dict | list[dict] | None:
        """
        Returns all servers if no server_id is provided.
        """
        if server_id is None:
            with conn.cursor() as cur:
                cur.execute("SELECT server_id,servername,language,play_maxlen FROM discord_servers")
                db_result = cur.fetchall()
            return [{
                'server_id': row[0],
                'servername': row[1],
                'language': row[2],
                'play_maxlen': row[3]
            } for row in db_result]

        with conn.cursor() as cur:
            cur.execute(
                "SELECT server_id,servername,language,play_maxlen FROM discord_servers " +
                "WHERE (server_id=%(server_id)s);",
                {'server_id': server_id}
            )
            db_result = cur.fetchall()
        if not db_result:
            return None
        return {
            'server_id': server_id,
            'servername': db_result[0][1],
            'language': db_result[0][2],
            'play_maxlen': db_result[0][3]
        }

    @staticmethod
    def add_server(conn: connection, server_id: int, name="unknown"):
        """
        Adds server to the database.
        """
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO discord_servers (server_id,servername) " +
                "VALUES (%(server_id)s,%(name)s) " +
                "ON CONFLICT (server_id) DO UPDATE " +
                "SET servername = %(name)s;",
                {'server_id': server_id, 'name': name}
            )
        return

    @staticmethod
    def get_admin_groups(conn: connection, server_id: int) -> list[str]:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT group_name FROM discord_server_admin_groups WHERE server_id=%(server_id)s",
                {'server_id': server_id}
            )
        return [x[0] for x in cur.fetchall()]

    @staticmethod
    def add_admin_group(conn: connection, server_id: int, group_name: str) -> int:
        existing_groups = Database.get_admin_groups(conn, server_id)

        # check if group already exists
        if group_name in existing_groups:
            return 409

        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO discord_server_admin_groups (server_id, group_name)" +
                "VALUES (%(server_id)s,%(group_name)s)",
                {'server_id': server_id, 'group_name': group_name}
            )
        return 200

    @staticmethod
    def remove_admin_group(conn: connection, server_id: int, group_name: str) -> int:
        existing_groups = Database.get_admin_groups(conn, server_id)

        if group_name not in existing_groups:
            return 404

        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM discord_server_admin_groups " +
                "WHERE server_id=%(server_id)s AND " +
                "group_name=%(group_name)s;",
                {'server_id': server_id, 'group_name': group_name}
            )
        return 200

    @staticmethod
    def get_play_max_len(conn: connection, server_id: int) -> int:
        """Returns max length of randomly chosen sound
        """
        with conn.cursor() as cur:
            cur.execute(
                "SELECT play_maxlen FROM discord_servers WHERE server_id = %(server_id)s",
                {'server_id': server_id}
            )
            db_result = cur.fetchall()
        return db_result[0][0]

    @staticmethod
    def set_play_max_len(conn: connection, server_id: int, maxlen: int):
        """Sets maximum amount of sound file if chosen randomly
        """
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE discord_servers " +
                "SET play_maxlen = %(play_maxlen)s " +
                "WHERE server_id = %(server_id)s;",
                {'play_maxlen': maxlen, 'server_id': server_id}
            )
        return

    # -- "private" functions

    @staticmethod
    def __ensure_tables(conn: connection):
        """Executes all sql files provided in data/schemas, starting with base.sql
        """
        schema_folder = config.Config().folders["data"].joinpath("schemas")

        # create base schema
        logging.info("Recreating database schema '%s'", "base.sql")
        with conn.cursor() as cur:
            cur.execute(open(schema_folder.joinpath("base.sql"), "r").read())

        # create all other schemas
        schemas = [x for x in os.listdir(schema_folder) if x != "base.sql" and x.endswith(".sql")]

        for schema in schemas:
            logging.info("Recreating database schema '%s'", schema)
            current_path = schema_folder.joinpath(schema)

            with conn.cursor() as cur:
                cur.execute(open(current_path, "r").read())


class Brotato:
    """
    Database class that handles access concerning the brotato module.
    """
    @staticmethod
    def get_brotato_char(conn: connection, char="") -> list[dict] | None:
        """
        Returns single char if string provided, all if not
        """
        result_list = []

        # no input given
        if char == "":
            with conn.cursor() as cur:
                cur.execute("SELECT char_id,name_en,name_de FROM brotato_chars;")
                db_result = cur.fetchall()
            for row in db_result:
                result_list.append({'id': row[0], 'name_en': row[1], 'name_de': row[2]})
            if len(result_list) == 0:
                return None
            return result_list

        # input given
        with conn.cursor() as cur:
            cur.execute(
                "SELECT char_id,name_en,name_de FROM brotato_chars " +
                "WHERE LOWER(name_de) = LOWER(%(name)s) OR " +
                "LOWER(name_en) = LOWER(%(name)s);",
                {'name': char}
            )
            db_result = cur.fetchone()
        if db_result is None:
            return None
        return [{'id': db_result[0], 'name_en': db_result[1], 'name_de': db_result[2]}]

    @staticmethod
    def add_brotato_char(conn: connection, char: str):
        """
        Adds new character to database
        """
        if Brotato.get_brotato_char(conn, char) is not None:
            return
        with conn.cursor() as cur:
            cur.execute("INSERT INTO brotato_chars (name_de) VALUES (%(name)s);", {'name': char})
        return

    @staticmethod
    def get_brotato_highscore(
            conn: connection, diff: int, character: str | None, guild_id: int
    ) -> tuple[list[tuple], list] | None:
        """Get highscores from database

        Args:
            conn: connection to database
            diff: difficulty
            character: name of the character
            guild_id: discord server id

        Returns:
            tuple[list[tuple],list]: ([(highscore,...),(highscore,...)],[heading1,heading2,...])
        """
        # handle if char is set/not set
        if character is not None:
            char_id = Brotato.get_brotato_char(conn, character)
            if char_id is not None:
                char_id = char_id[0]['id']
        else:
            char_id = None

        # this ist horrible, but sql commands with strings as parameters scare me
        if diff is None:
            if char_id is None:
                # diff: no, char, no
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT du.name,br.wave,br.danger,bc.name_de FROM brotato_runs br " +
                        "INNER JOIN discord_users du ON du.user_id = br.user_id " +
                        "INNER JOIN brotato_chars bc ON bc.char_id = br.char_id " +
                        "WHERE br.server_id=%(server_id)s " +
                        "ORDER BY wave DESC " +
                        "LIMIT 20;",
                        {'server_id': guild_id}
                    )
                    result = cur.fetchall()
                    heading = ["Spieler", "Welle", "Gefahr", "Charakter"]
            else:
                # diff: no, char yes
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT du.name,br.wave,br.danger FROM brotato_runs br " +
                        "INNER JOIN discord_users du ON du.user_id = br.user_id " +
                        "INNER JOIN brotato_chars bc ON bc.char_id = br.char_id " +
                        "WHERE br.char_id=%(char_id)s " +
                        "AND br.server_id=%(server_id)s " +
                        "ORDER BY wave DESC " +
                        "LIMIT 20;",
                        {'char_id': char_id, 'server_id': guild_id},
                    )
                    result = cur.fetchall()
                    heading = ["Spieler", "Welle", "Gefahr"]
        else:
            if char_id is None:
                # diff: yes, char, no
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT du.name,br.wave,bc.name_de FROM brotato_runs br " +
                        "INNER JOIN discord_users du ON du.user_id = br.user_id " +
                        "INNER JOIN brotato_chars bc ON bc.char_id = br.char_id " +
                        "WHERE br.danger=%(danger)s " +
                        "AND br.server_id=%(server_id)s " +
                        "ORDER BY wave DESC " +
                        "LIMIT 20;",
                        {'danger': diff, 'server_id': guild_id}
                    )
                    result = cur.fetchall()
                    heading = ["Spieler", "Welle", "Charakter"]
            else:
                # diff: yes, char, yes
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT du.name,br.wave FROM brotato_runs br " +
                        "INNER JOIN discord_users du ON du.user_id = br.user_id " +
                        "INNER JOIN brotato_chars bc ON bc.char_id = br.char_id " +
                        "WHERE br.danger=%(diff)s " +
                        "AND br.char_id=%(char_id)s " +
                        "AND br.server_id=%(server_id)s " +
                        "ORDER BY wave DESC " +
                        "LIMIT 20;",
                        {"diff": diff, "char_id": char_id, 'server_id': guild_id}
                    )
                    result = cur.fetchall()
                    heading = ["Spieler", "Welle"]
        if result is None:
            return None
        return result, heading

    @staticmethod
    def add_brotato_run(conn: connection, char: str, wave: int, danger: int, user_id: int, server_id: int):
        """Creates new brotato run in the database

        Args:
            conn: Database connection
            char: _description_
            wave: _description_
            danger: _description_
            user_id: _description_
            server_id: _description_
        """
        char_id = Brotato.get_brotato_char(conn, char)[0]['id']

        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO brotato_runs (user_id,server_id,char_id,wave,danger,timestamp) " +
                "VALUES (%(user_id)s,%(server_id)s,%(char_id)s,%(wave)s,%(danger)s,%(timestamp)s);",
                {
                    'user_id': user_id,
                    'server_id': server_id,
                    'char_id': char_id,
                    'wave': wave,
                    'danger': danger,
                    'timestamp': int(time.time())
                }
            )


class FileCon:
    """
    Database class that handles access to files and tags
    """
    @staticmethod
    def add_file(conn: connection, file: dataclasses.File) -> int:
        """
        Adds file information to the database, this function expects the input data to be correct!
        """
        with conn.cursor() as cur:
            cur.execute(
                "insert into files (file_size, server_id, uploader_id, display_name, file_name, file_hash, seconds, "
                "deleted) values (%(size)s, %(server_id)s, %(uploader_id)s, %(display_name)s, %(name)s, %(hash)s, "
                "%(seconds)s, %(deleted)s) returning file_id",
                {
                    "size": file.size,
                    "server_id": file.guild_id,
                    "uploader_id": file.user_id,
                    "display_name": file.display_name,
                    "name": file.file_name,
                    "hash": file.file_hash,
                    "seconds": file.seconds,
                    "deleted": False,
                }
            )
            file_id = cur.fetchone()[0]
        if file.tags:
            for tag in file.tags:
                FileCon.link_tag(conn, file_id, tag)
        return file_id

    @staticmethod
    def get_file(conn: connection, **kwargs) -> list[dataclasses.File]:
        """
        visible: only return files visible to the user
        Uses kwargs for WHERE LIKE lookup, they are chained with AND operators
        (file_id, size, server_id, uploader_id, display_name, file_name, hash, public)
        """
        # Check if provided kwargs are valid use cases
        with conn.cursor() as cur:
            cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'files'")
            columns = [x[0] for x in cur.fetchall()]

        query = ""
        for key, value in kwargs.items():
            if key not in columns:
                raise TypeError(f"Unexpected keyword argument '{key}'")
            query = FileCon.__build_argument(key, query)

        # build SQL request
        with conn.cursor() as cur:
            cur.execute(
                "SELECT file_id,file_size,server_id,uploader_id,display_name,file_name,file_hash, "
                "seconds FROM files " + query,
                kwargs
            )
            db_result = cur.fetchall()
        files = []
        for row in db_result:
            files.append(
                dataclasses.File(
                    id=row[0],
                    size=row[1],
                    guild_id=row[2],
                    user_id=row[3],
                    display_name=row[4],
                    file_name=row[5],
                    file_hash=row[6],
                    seconds=row[7],
                    tags=()  # TODO fetch tags
                )
            )
        return files

    @staticmethod
    def mark_file_deleted(db_con, file_id: int, deleted: bool):
        """
        Takes file id and marks affected file as deleted.
        """
        with db_con.cursor() as cur:
            cur.execute(
                'update files set deleted = %(deleted)s, deletion_date = now() where file_id = %(file_id)s',
                {
                    'file_id': file_id,
                    'deleted': deleted,
                }
            )

    @staticmethod
    def __build_argument(keyword: str, query: str = "") -> str:
        """
        Creates additional WHERE statements in order for query to be somewhat dynamic
        """
        if query:
            query += f" AND {keyword} = %({keyword})s"
            return query
        else:
            return f"WHERE {keyword} = %({keyword})s"

    @staticmethod
    def add_tag(conn: connection, tag_name: str) -> int:
        """
        Creates a new tag in the database, returns the tag id
        """
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tags (tag_name) VALUES (%(tag_name)s) RETURNING tag_id",
                {"tag_name": tag_name}
            )
            return cur.fetchone()[0]

    @staticmethod
    def get_tag(conn: connection, identifier: int | str) -> list[tuple[int, str]]:
        """
        Gets tag from the database, no parameter for every tag.
        int -> by id
        str -> by name
        """
        if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
            query = "SELECT tag_id,tag_name FROM tags WHERE tag_id=%(identifier)s"
        elif isinstance(identifier, str):
            query = "SELECT tag_id,tag_name FROM tags WHERE tag_name=%(identifier)s"
        elif identifier is None:
            query = "SELECT tag_id,tag_name FROM tags"
        else:
            raise Exception("Tag identifier must be int or string")

        with conn.cursor() as cur:
            cur.execute(
                query,
                {"identifier": identifier}
            )
            return cur.fetchall()

    @staticmethod
    def link_tag(conn: connection, file_id: int, tag: int | str):
        """
        Links tag to file. If both id and name are set id takes priority.
        Creates tags if they don't exist yet.
        """
        if not FileCon.get_file(conn, file_id=file_id):
            raise Exception("Requested file does not exist!")

        # create tag in db if it doesn't exist already
        if not (db_tag := FileCon.get_tag(conn, tag)) and isinstance(tag, str):
            db_tag = (FileCon.add_tag(conn, tag), tag)
        # TODO: fix this! fix what??
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO files_tags (file_id,tag_id) VALUES (%(file_id)s,%(tag)s)",
                {"file_id": file_id, "tag": db_tag[0]}
            )


class User:
    """
    Database class for users
    """
    @staticmethod
    def add_user(conn: connection, user_id: int, user_name: str):
        """
        Allows adding a new user to the database.
        Updates on conflict.
        """
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO discord_users (user_id,name) VALUES (%(id)s,%(name)s) " +
                "ON CONFLICT (user_id) DO UPDATE " +
                "SET name = %(name)s;",
                {'id': user_id, 'name': user_name}
            )

    @staticmethod
    def delete_user(conn: connection, user_id: str):
        pass
        # TODO delete user and remove all associations

    @staticmethod
    def get_user(conn: connection, user_id: int, server_id: int = None) -> dict | None:
        """
        Retrieves specified user from the database.
        """
        with conn.cursor() as cur:
            cur.execute("SELECT user_id,name,uploader FROM discord_users WHERE user_id=%s;", (user_id,))
            result = cur.fetchone()

        if result is None:
            return None
        if not server_id:
            return {"id": result[0], "name": result[1], "uploader": result[2]}

        # get server's display name
        with conn.cursor() as cur:
            cur.execute(
                "SELECT displayname FROM discord_user_displaynames " +
                "WHERE user_id=%(user_id)s AND server_id=%(server_id)s;",
                {'user_id': user_id, 'server_id': server_id}
            )
            display_name = cur.fetchone()
        # if no name found fall back to username
        result_dict = {'id': result[0], 'uploader': result[2]}
        if display_name is None:
            result_dict['name'] = result[1]
        result_dict['name'] = display_name
        return result_dict

    @staticmethod
    def add_user_display_name(conn: connection, user_id: int, server_id: int, name: str):
        """
        Adds a user's display name to the database.
        """
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO discord_user_displaynames (user_id,server_id,displayname) " +
                "VALUES (%(user_id)s,%(server_id)s,%(displayname)s) " +
                "ON CONFLICT (user_id,server_id) DO UPDATE " +
                "SET displayname = %(displayname)s",
                {'user_id': user_id, 'server_id': server_id, 'displayname': name}
            )

    @staticmethod
    def user_ensure(conn: connection, user: discord.Member):
        """
        Creates user if they do not exist yet.
        """
        if not User.get_user(conn, user_id=user.id):
            User.add_user(conn, user_id=user.id, user_name=user.name)
            User.add_user_display_name(conn, user_id=user.id, server_id=user.guild.id, name=user.name)

    @staticmethod
    def user_set_uploader(conn: connection, user: discord.Member, uploader: bool):
        User.user_ensure(conn, user)
        with conn.cursor() as cur:
            cur.execute(
                "update discord_users set uploader = %(status)s WHERE user_id = %(id)s;",
                {'id': user.id, 'status': uploader}
            )
