import logging, os, pathlib, random
import discord
from discord.ext import commands
from util import config, filemgr, voice

class Sounds(commands.Cog):
    SOUND_FOLDER: pathlib.Path
    
    def __init__(self, bot, settings: config.Config):
        self.bot = bot
        self.SOUND_FOLDER = settings.folders["sounds_custom"]

    @discord.slash_command(name="play", description="Plays sound in your current channel.")
    async def play(self, ctx: discord.ApplicationContext, sound_name: discord.Option(str, "Name of the soundfile you want to play. Leave empty for random sound.", default="", name="sound")):
        logging.debug("<command> - play")
        
        # is channel joinable
        if ctx.voice_client is not None:
            if ctx.author.voice.channel != ctx.voice_client.channel and not await voice.is_joinable(ctx, ctx.author.voice.channel):
                return
        
        if ctx.author.voice is None:
            await ctx.respond("Join a channel to use this command.")
            return

        # choose sound to play
        if sound_name == "":
            sound = self.__choose_sound()
        else:
            sound = self.__choose_sound(sound_name)

        # if still no sound was found, check for matching foldername instead
        if sound is None:
            file = filemgr.search_files(filemgr.get_folders(self.SOUND_FOLDER), sound_name)
            sound = self.__choose_sound(folder=file)

        if sound is None:
            await ctx.respond("No sound found")
            return
        await self.play_sound(ctx, sound)
        return

    @discord.slash_command(name="folder", description="Plays random sound from given folder.")
    async def folder(self, ctx: discord.ApplicationContext, folder_name: discord.Option(str, "Name of folder to play sound from", name="folder")):
        if ctx.voice_client is not None:
            if ctx.author.voice.channel != ctx.voice_client.channel and not await voice.is_joinable(ctx, ctx.author.voice.channel):
                return
        if ctx.author.voice is None:
            await ctx.respond("Join a channel to use this command.")
            return
        
        if folder_name == "":
            await ctx.respond("No folder name provided")
            return
        
        # choose matching folder
        result = filemgr.search_files(filemgr.get_folders(self.SOUND_FOLDER), folder_name)
        
        sound = self.__choose_sound(folder=result)

        if sound is None:
            await ctx.respond("No sound found")
            return
        await self.play_sound(ctx, sound)

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


    @discord.slash_command(name="soundlist", description="List available sounds.")
    async def soundlist(self, ctx: discord.ApplicationContext):
        '''Returns embed with list of found sounds, and their folders.'''
        # https://discord.com/developers/docs/resources/channel#embed-object
        # TODO Logic to handle too big results (see link above for requirements)

        result_dict = {
            "fields" : []
            }

        # Handle root
        folders = []
        files = []
        for file in self.SOUND_FOLDER.iterdir():
            if file.is_file():
                files.append(file)
                continue
            if file.is_dir():
                folders.append(file)
        result_dict["fields"].append({"name": "Allgemein", "value": "\r".join([x.stem for x in files])})

        # Handle folders within root
        for folder in folders:
            files = filemgr.get_files_rec(folder)
            result_dict["fields"].append({"name": folder.stem, "value": "\r".join([x.stem for x in files])})
            
        await ctx.respond(embed=discord.Embed.from_dict(result_dict))


    def __choose_sound(self, name: str = None, folder: pathlib.Path = None) -> tuple[pathlib.Path,float] | None:
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
            return filemgr.get_random_file(path)
        
        # Search for closest match compared to string.
        sound_files = filemgr.get_files_rec(path)
        found_sound = filemgr.search_files(sound_files, name)

        if found_sound is None:
            return None
        # TODO ensure this is actually a playable sound file
        return found_sound

    async def play_sound(self, ctx, sound: pathlib.Path):
        '''Actually playing the sound. This expects the provided file to work!'''
        
        await ctx.respond(f"Playing '{sound.stem}'")
        await voice.join_channel(ctx, ctx.author.voice.channel)
        await voice.play_sound(ctx, f"{str(sound)}")


if __name__=="__main__":
    logging.error("This file isn't supposed to be executed!")
    exit()