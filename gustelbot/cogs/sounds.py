"""
This file implements all commands regarding sounds.
"""
import logging
import math
import pathlib
import random
import string
import tempfile
import traceback
import typing
from datetime import timedelta
from difflib import SequenceMatcher

import discord
from discord.ext import commands
from discord.ext import tasks
from psycopg2.extensions import connection

from gustelbot.util import config
from gustelbot.util import dataclasses
from gustelbot.util import filemgr
from gustelbot.util import voice
from gustelbot.util.database import Database, FileCon, User


class Sounds(commands.Cog):
    SOUND_FOLDER: pathlib.Path
    db: Database

    def __init__(self, bot: commands.Bot, settings: config.Config):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.settings = settings
        self.SOUND_FOLDER = settings.folders["sounds_custom"]
        self.check_files.start()

    @tasks.loop(seconds=120)
    async def check_files(self):
        """
        Check if local files are up-to-date with
        """
        db_con = Database.new_connection()

        db_expected_files = FileCon.get_file(db_con, deleted=False)
        db_expected_file_set = {x.file_name for x in db_expected_files}

        db_deleted_files = FileCon.get_file(db_con, deleted=True)
        db_deleted_file_set = {x.file_name for x in db_deleted_files}

        local_files = {x.name for x in self.SOUND_FOLDER.glob('**/*')}

        # check missing files
        missing_files = db_expected_file_set - local_files
        for missing_file in missing_files:
            file_id = FileCon.get_file(db_con, file_name=missing_file)
            FileCon.mark_file_deleted(db_con, file_id[0].id, True)

        # surplus files
        surplus_files = local_files - db_expected_file_set
        files_to_restore = surplus_files.union(db_deleted_file_set)
        local_file_paths = list(self.SOUND_FOLDER.glob('**/*'))
        restored_files = []
        for local_file in local_file_paths:
            # check if file is correct
            if local_file.name in files_to_restore:
                db_file = FileCon.get_file(db_con, file_name=local_file.name)
                # if hash is correct, set as not deleted
                if db_file and db_file[0].file_hash == filemgr.calculate_md5(local_file):
                    FileCon.mark_file_deleted(db_con, db_file[0].id, False)
                    restored_files.append(db_file[0].file_name)
        db_con.commit()
        if missing_files:
            self.logger.info(f"Marked the files {missing_files} as deleted.")
        if restored_files:
            self.logger.info(f"Marked the files {restored_files} as restored.")

    @discord.slash_command(name="play", description="Plays sound in your current channel.")
    @discord.option(name="sound_name", description="Name of the sound, leave empty for random choice", required=False)
    async def play(self, ctx: discord.ApplicationContext, sound_name: str):
        """
        Play command, searches for random file if no name provided
        """
        db_con = Database.new_connection()

        if not (response := (await voice.is_joinable(ctx)))[0]:
            await ctx.respond(response[1])
            return
        # choose sound to play
        if sound_name:
            sound = Sounds.__choose_sound(
                db_con, ctx.author.id, ctx.guild_id, search_str=sound_name
            )
        else:
            sound = Sounds.__choose_sound(
                db_con, ctx.author.id, ctx.guild_id, Database.get_play_max_len(db_con, ctx.guild.id)
            )

        # if still no sound was found, check for matching tag instead
        # TODO: implement retrieval of file by tag

        if sound is None:
            await ctx.respond("No matching sound found")
            return

        await Sounds.play_sound(ctx, pathlib.Path(self.SOUND_FOLDER, sound.file_name), sound.display_name)

    @discord.slash_command(name="stop", description="Stops playback")
    async def stop(self, ctx: discord.ApplicationContext):

        if ctx.voice_client is None:
            await ctx.respond("I am not connected to any channel.")
            return

        if not ctx.voice_client.is_playing():
            await ctx.respond("There is nothing to stop")
            return

        ctx.voice_client.stop()
        await ctx.respond("⏹️ Playback stopped!")

    @discord.slash_command(name="disconnect", description="Disconnects bot from channel.")
    async def disconnect(self, ctx: discord.ApplicationContext):
        # Disconnect bot from current channel
        logging.debug("<command> - disconnect")

        if ctx.voice_client is None:
            await ctx.respond("I am not connected to any channel.")
            return

        ctx.voice_client.stop()
        await ctx.respond("Disconnecting...")
        await ctx.voice_client.disconnect(force=False)

    sound_group = discord.SlashCommandGroup(name="sound", description="Information and commands regarding sounds")

    @sound_group.command(name="list", description="Lists all sounds available")
    async def sound_list(self, ctx: discord.ApplicationContext):
        """
        Returns Embed that contains all sounds available
        """
        db_con = Database.new_connection()
        all_files = [x.display_name for x in FileCon.get_file(db_con, deleted=False)]
        result_dict = {
            "fields": [{"name": "All available files", "value": "\r".join(all_files)}],
        }
        await ctx.respond(embed=discord.Embed.from_dict(result_dict))

    @sound_group.command(name="upload", description="Uploads sound to GustelBot")
    @discord.option(name="sound_file", type=discord.Attachment, description="Sound file to upload.")
    @discord.option(name="sound_name", description="Name of the sound.")
    @discord.option(name="tags", description="Comma seperated list of tags to apply", required=False)
    async def sound_upload(
            self, ctx: discord.ApplicationContext,
            sound_file: discord.Attachment,
            sound_name: str,
            tags: str
    ):
        """
        Allows users to upload a new sound to GustelBot
        """
        db_con = Database.new_connection()

        if not (User.get_user(db_con, ctx.author.id)['uploader'] or self.settings.is_superuser(ctx.author.id)):
            await ctx.respond("You are not allowed to upload sounds to GustelBot.")
            return

        if not sound_file.content_type.startswith('audio/'):
            await ctx.respond('Failed to upload file: Not a valid audio file')
            return

        if sound_file.size > 50000000:
            await ctx.respond('Failed to upload file: Maximum size is 50MB')
            return

        if len(sound_file.filename) > 25:
            await ctx.respond('Failed to upload file: Maximum filename length is 25 characters')
            return

        if ',' in sound_name:
            await ctx.respond("The ',' symbol is not allowed in sound names.")

        if tags:
            tag_tup = tags.split(',')
            for tag in tag_tup:
                if tag.isdigit():
                    await ctx.respond("Tags cannot be numbers, some will be ignored.")
            tag_tup = tuple([x.strip() for x in tag_tup if not x.isdigit() and x])
        else:
            tag_tup = None

        # check if provided display name is already in use (and visible)
        if FileCon.get_file(db_con, display_name=sound_name):
            await ctx.respond(f'**Error**: The Filename `{sound_name}` is already in use!')
            return

        # save file to tmp and attach random string to provided name
        await ctx.respond('Uploading sound to GustelBot...')
        random_str = string.ascii_lowercase
        random_str = "".join(random.sample(random_str, 5))
        tmp_file_path = pathlib.Path(f'{tempfile.gettempdir()}/{random_str}+{sound_file.filename}')
        await sound_file.save(fp=tmp_file_path)

        # calculate hash of file and check db if already exists
        file_md5 = filemgr.calculate_md5(tmp_file_path)
        if existing_file := FileCon.get_file(db_con, file_hash=file_md5):
            existing_file = existing_file[0]
            await ctx.respond(f'Your upload `{sound_name}` already exists as `{existing_file.display_name}`')
            return

        # create new file
        self.__create_sound_file(
            db_con,
            dataclasses.File(
                size=tmp_file_path.stat().st_size,
                guild_id=ctx.guild.id,
                user_id=ctx.author.id,
                display_name=sound_name,
                file_name=tmp_file_path.name,
                file_hash=file_md5,
                seconds=math.floor(filemgr.get_sound_length(tmp_file_path)),
                tags=tag_tup
            ),
            tmp_file_path
        )
        db_con.commit()
        await ctx.respond(f'Sound `{sound_name}` successfully uploaded to GustelBot')

    def __create_sound_file(self, db_con: connection, file: dataclasses.File, source_file: pathlib.Path):
        """
        Establishes a new Sound file in the database and copies it to the folder.
        """
        # move file to proper folder
        try:
            filemgr.move_to_folder(source_file, self.SOUND_FOLDER)
        except (FileNotFoundError, NotADirectoryError):
            logging.error(f'Failed to move file to proper folder: {traceback.format_exc()}')
        try:
            FileCon.add_file(db_con, file)
            db_con.commit()
        except Exception as e:
            self.logger.error(f'Failed to add file {source_file.name} to database: {traceback.format_exc()}')
            pathlib.Path(self.SOUND_FOLDER, source_file.name).unlink()
            raise e

    @sound_upload.error
    async def on_sound_upload_error(self, ctx: discord.ApplicationContext, _: discord.DiscordException):
        if ctx.response:
            print("amogus")
        else:
            print("nicht amogus")
        logging.error(traceback.format_exc())
        await ctx.respond('Internal server error.')

    @sound_group.command(name='details', description='Returns details about a sound.')
    @discord.option(name="sound_name", description="Name of the sound.")
    async def sound_details(self, ctx: discord.ApplicationContext, sound_name: str):
        """
        Returns details about a sound, same behaviour as play
        """
        sound = self.__choose_sound(ctx.author.id, ctx.guild_id, search_str=sound_name)

        if not sound:
            await ctx.respond("The sound you specified cannot be found.")
            return

        details = [
            f"`name  :` {sound.display_name}",
            f"`id    :` {sound.id}",
            f"`length:` {timedelta(seconds=sound.seconds)}",
            f"`public:` {sound.public}",
            f"`tags  :` {', '.join(sound.tags)}",
        ]
        embed = {
            "title": "GustelBot Song Details",
            "description": "\r".join(details)
        }

        await ctx.respond(embed=discord.Embed.from_dict(embed))

    @staticmethod
    def __choose_sound(
            conn: connection,
            user_id: int,
            guild_id: int,
            max_len: typing.Optional[int] = None,
            search_str: str = None,
            tags: list[str] = None
    ) -> typing.Optional[dataclasses.File]:
        """
        Searches database for fitting sound and returns path to sound file.
        """
        all_sounds = FileCon.get_file(conn, deleted=False)

        # if max_len is set filter list for that
        if max_len:
            all_sounds = [sound for sound in all_sounds if sound.seconds <= max_len]

        # if tags are provided, filter by the tags
        if tags:
            for tag in tags:
                all_sounds = [sound for sound in all_sounds if tag in sound.tags]

        # if search string is provided, rank by likelihood of being a match
        if search_str:
            all_sounds = [
                (sound,
                 SequenceMatcher(
                     None,
                     sound.display_name.lower(),
                     search_str.lower()
                 ).ratio()) for sound in all_sounds
            ]
            all_sounds = sorted(all_sounds, key=lambda x: x[1], reverse=True)

        if len(all_sounds) == 0:
            return None
        if isinstance(all_sounds[0], tuple):
            return all_sounds[0][0] if all_sounds[0][1] >= 0.65 else None
        else:
            return all_sounds[0]

    @staticmethod
    async def play_sound(ctx, sound: pathlib.Path, name: str = None):
        """
        Actually playing the sound. This expects the provided file to work!
        If a name is provided it will be announced.
        """
        if name:
            await ctx.respond(f"Playing '{name}'")
        if not sound.exists():
            await ctx.respond("Error: The specified sound does not exist.")
            return
        await voice.join_channel(ctx, ctx.author.voice.channel)
        await voice.play_sound(ctx, f"{str(sound)}")

    @staticmethod
    async def join_preparation(ctx: discord.ApplicationContext) -> bool:
        """Checks if channel has to be joined, returns False if no or not possible.
        This function also sends a reply to notify if joining was not possible.

        Args:
            ctx: _description_
        """
        if ctx.author.voice and ctx.author.voice.channel != ctx.voice_client.channel:
            return True
        return (await voice.is_joinable(ctx))[0]


if __name__ == "__main__":
    logging.error("This file isn't supposed to be executed!")
    exit()
