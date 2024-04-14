"""
This file implements all commands regarding sounds.
"""
# default
import logging
import pathlib
import random
import string
import tempfile
import traceback
# pip
import discord
from discord.ext import commands
# internal
from gustelbot.util import config
from gustelbot.util import database
from gustelbot.util import filemgr
from gustelbot.util import voice


class Sounds(commands.Cog):
    SOUND_FOLDER: pathlib.Path
    db: database.Database

    def __init__(self, bot: commands.Bot, settings: config.Config, db: database.Database):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.SOUND_FOLDER = settings.folders["sounds_custom"]
        self.db = db

    @discord.slash_command(name="play", description="Plays sound in your current channel.")
    @discord.option(name="sound_name", description="Name of the sound, leave empty for random choice", required=False)
    async def play(self, ctx: commands.Context | discord.ApplicationContext, sound_name: str):
        """
        Play command, searches for random file if no name provided
        """
        if not (response := (await voice.is_joinable(ctx)))[0]:
            await ctx.respond(response[1])
            return
        # choose sound to play
        if sound_name == "":
            sound = self.__choose_sound(maxlen=self.db.get_play_maxlen(ctx.guild.id))
        else:
            sound = self.__choose_sound(name=sound_name, maxlen=0)

        # if still no sound was found, check for matching foldername instead
        if sound is None:
            file = filemgr.search_files(filemgr.get_folders(self.SOUND_FOLDER), sound_name)
            sound = self.__choose_sound(folder=file, maxlen=self.db.get_play_maxlen(ctx.guild.id))

        if sound is None:
            await ctx.respond("No sound found")
            return
        await Sounds.play_sound(ctx, sound)
        return

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

        # This is kinda weird: ctx.voic_client is an object with type: voice_client.VoiceClient
        if ctx.voice_client is None:
            await ctx.respond("I am not connected to any channel.")
            return

        ctx.voice_client.stop()
        await ctx.respond("Disconnecting...")
        await ctx.voice_client.disconnect()

    sound_group = discord.SlashCommandGroup(name="sound", description="Information and commands regarding sounds")

    @sound_group.command(name="list", description="Lists all sounds available")
    async def sound_list(self, ctx: commands.Context | discord.ApplicationContext):
        """
        Returns Embed that contains all sounds available
        """
        result_dict = {
            "fields": [{"name": "Amogus", "value": "\r".join(["yellow", "blue", "green", "red"])}],
        }
        await ctx.respond(embed=discord.Embed.from_dict(result_dict))

    @sound_group.command(name="upload", description="Uploads sound to GustelBot")
    @discord.option(name="sound_file", type=discord.Attachment, description="Sound file to upload.")
    @discord.option(name="sound_name", description="Name of the sound.")
    @discord.option(name="tags", description="Comma seperated list of tags to apply", required=False)
    @discord.option(name="private", description="Only show sound on this server", default=False, required=False)
    async def sound_upload(
            self, ctx: commands.Context | discord.ApplicationContext,
            sound_file: discord.Attachment,
            sound_name: str,
            tags: str,
            private: bool
    ):
        """
        Allows users to upload a new sound to GustelBot
        """
        if not sound_file.content_type.startswith('audio/'):
            await ctx.respond('Failed to upload file: Not a valid audio file')
            return

        if sound_file.size > 50000000:
            await ctx.respond('Failed to upload file: Maximum size is 50MB')
            return

        if len(sound_file.filename) > 100:
            await ctx.respond('Failed to upload file: Maximum filename length is 100 characters')
            return

        if tags:
            tags = tags.split(',')
            tags = [x.strip() for x in tags]
        db_con = database.File()

        # check if provided display name is already in use (and visible)
        if file := db_con.get_file(display_name=sound_name):
            if db_con.is_visible(ctx.guild.id, file[0][0]):
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
        if existing_file := db_con.get_file(file_hash=file_md5):
            # check if the already existing version is available from this server
            if db_con.is_visible(existing_file[0][0], ctx.author.guild.id):
                await ctx.respond(f'File {sound_name} already exists as {existing_file[4]}')
                return
            try:
                self.__create_sound_link(existing_file[0], sound_name, tags, private)
            except Exception:
                self.logger.error(f"Failed to create link for sound '{sound_name}': {traceback.format_exc()}")
                await ctx.respond('Internal server error')
            await ctx.respond(f'Sound {sound_name} successfully uploaded to GustelBot')
            return

        try:
            self.__create_sound_file(
                tmp_file_path,sound_name, tags, private,
                file_md5, db_con, ctx.guild.id, ctx.author.id
            )
        except Exception:
            await ctx.respond('Internal server error')
            return

    def __create_sound_file(
            self,
            sound_file: pathlib.Path,
            sound_name: str,
            tags: list[str],
            private: bool,
            md5: str,
            db_con: database.File,
            guild_id: int,
            uploader_id: int
    ):
        """
        Establishes a new Sound file in the database and copies it to the folder.
        """
        file_size = sound_file.stat().st_size

        # move file to proper folder
        try:
            filemgr.move_to_folder(sound_file, self.SOUND_FOLDER)
        except (FileNotFoundError, NotADirectoryError):
            logging.error(f'Failed to move file to proper folder: {traceback.format_exc()}')

        try:
            db_con.add_file(
                tags=tags,
                display_name=sound_name,
                file_size=file_size,
                file_name=sound_file.name,
                file_hash=md5,
                public=(not private),
                server_id=guild_id,
                uploader_id=uploader_id
            )
        except Exception as e:
            self.logger.error(f'Failed to add file {sound_file.name} to database: {traceback.format_exc()}')
            pathlib.Path(self.SOUND_FOLDER, sound_file.name).unlink()
            raise e

    @sound_upload.error
    async def on_sound_upload_error(self, ctx: discord.ApplicationContext, _: discord.DiscordException):
        await ctx.respond(f'Internal server error.')

    def __create_sound_link(self, existing_file: tuple, sound_name: str, tags: list[str], private: bool):
        """
        Creates a link for a file that already exists but was invisible to the user who added it.
        """

    def __choose_sound(
            self, name: str = None,
            folder: pathlib.Path = None,
            maxlen: int = 0) -> tuple[pathlib.Path, float] | None:
        """Chooses sound based on provided folder and search string.

        Args:
            name: keyword to search for. Defaults to random selection.
            folder: path to folder to search. Defaults to None.

        Returns:
            returns Path object to sound
        """

        if folder is not None:
            path = folder
        else:
            path = self.SOUND_FOLDER

        if name is None:
            return filemgr.get_random_file(path, maxlen)

        # Search for closest match compared to string.
        sound_files = filemgr.get_files_rec(path)
        found_sound = filemgr.search_files(sound_files, name)

        if found_sound is None:
            return None
        # TODO ensure this is actually a playable sound file
        return found_sound

    @staticmethod
    async def play_sound(ctx, sound: pathlib.Path(), message=True):
        """
        Actually playing the sound. This expects the provided file to work!
        """
        if message:
            await ctx.respond(f"Playing '{sound.stem}'")
        await voice.join_channel(ctx, ctx.author.voice.channel)
        await voice.play_sound(ctx, f"{str(sound)}")

    @staticmethod
    async def join_preparation(ctx: commands.Context | discord.ApplicationContext) -> bool:
        """Checks if channel has to be joined, returns False if no or not possible.
        This function also sends a reply to notify if joining was not possible.

        Args:
            ctx: _description_
        """
        if ctx.author.voice and ctx.author.voice.channel != ctx.voice_client.channel:
            return True
        return await voice.is_joinable(ctx)


if __name__ == "__main__":
    logging.error("This file isn't supposed to be executed!")
    exit()
