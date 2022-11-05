import logging, os, pathlib, random
import discord
from difflib import SequenceMatcher
from discord.ext import commands
from util import config, filemgr, voice

class Sounds(commands.Cog):
    SOUND_FOLDER: pathlib.Path
    
    def __init__(self, bot, settings: config.Config):
        logging.debug("<init> - sounds")

        self.bot = bot
        self.SOUND_FOLDER = settings.folders["sounds_custom"]


    @discord.slash_command(name="play", description="Plays sound in your current channel.")
    async def play(self, ctx: discord.ApplicationContext, sound_name: discord.Option(str, "Name of the soundfile you want to play. Leave empty for random sound.", default="", name="sound")):
        logging.debug("<command> - play")
        
        # Check if channel is joinable at all
        if ctx.voice_client is not None:
            if ctx.author.voice.channel != ctx.voice_client.channel and not await voice.is_joinable(ctx, ctx.author.voice.channel):
                return
        
        if ctx.author.voice is None:
            await ctx.respond("Join a channel to use this command.")
            return

        # in case any arguments have been provided
        if not sound_name == "":
            sound = self.choose_sound(sound_name)

            if sound is None:
                await ctx.respond("No sounds available.")
                return

            await self.play_sound(ctx, sound)
            return
        
        # No arguments provided
        sound = self.choose_sound()

        if sound is None:
            await ctx.respond("No matching sound found.")
            return

        await self.play_sound(ctx, sound)
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


    @discord.slash_command(name="soundlist", description="List available sounds.")
    async def soundlist(self, ctx: discord.ApplicationContext):
        # posts list of files in /sounds folder, without folder or extension.
        logging.debug("<command> - soundlist")
        
        # TODO only look for actual soundfiles
        found_files = filemgr.get_file_names(self.SOUND_FOLDER)

        if not found_files:
            await ctx.respond("No sounds found.")
            return

        # Build results into embed
        fields = [[]]
        field_size = 0
        current_field = 0
        
        for file in found_files:
            if field_size + len(file) < 900:
                fields[current_field].append(file)
                field_size += len(file)
            else:
                fields.append([])
                current_field += 1
                fields[current_field].append(file)
                field_size = len(file)
        
        # TODO make interaction with embed possible, e.g multiple pages.
        embed = discord.Embed(
            description="**The following sounds are currently available:**"
        )

        # Add each field to the embed
        i = 0
        for field in fields:
            if i < 2:
                embed.add_field(name="Sound", value='\n'.join(field), inline=True)

            i += 1

        #embed.add_field(name=" ", value=found_files, inline=True)
        #embed.add_field(name="chinchin", value="Was weiß ich denn.mp3 \nDrecksackblase", inline=True)
        embed.set_footer(text="Page 1/1")


        await ctx.respond(embed=embed)
        
        #await ctx.respond(f"**The following songs are available:**\n{reply_str}")


    def choose_sound(self, name: str = "") -> tuple:
        '''Chooses file by name (path, filename) (or randomly when no param is given.), returns None if nothing is found'''
        
        if name == "":
            return filemgr.get_random_file(self.SOUND_FOLDER)
        
        # Search for closest match compared to string.
        allSounds = filemgr.get_files_rec(self.SOUND_FOLDER)
        foundSounds = []

        for sound in allSounds:
            # remove suffix for matching
            sound_no_suffix = str(pathlib.Path(sound[1]).with_suffix(''))
            ratio = SequenceMatcher(None, name, sound_no_suffix).ratio()
            
            if ratio >= 0.65:
                foundSounds.append((sound, ratio))
        
        if not foundSounds:
            return None

        if len(foundSounds) == 1:
            return (foundSounds[0][0][0], foundSounds[0][0][1])

        # sort by ratio (desc)
        foundSounds.sort(key=lambda x:x[1], reverse=True)

        # multiple results, check if delta between first to is bigger than 10%
        if (foundSounds[0][1] - foundSounds[1][1]) >= 0.1:
            return (foundSounds[0][0][0], foundSounds[0][0][1])
        
        # if too close, choose randomly between the 3 closest results
        i = 0
        lastRoll = []

        # finding: ((path, name), ratio)
        for finding in foundSounds:
            lastRoll.append(finding)
            i += 1
            if i == 3:
                break
        
        return random.choice(lastRoll)[0]


    async def play_sound(self, ctx, sound):
        '''Actually playing the sound. This expects the provided file to work!'''
        
        await ctx.respond(f"Playing '{pathlib.Path(sound[1]).with_suffix('')}'")
        await voice.join_channel(ctx, ctx.author.voice.channel)
        await voice.play_sound(ctx, f"{sound[0]}{os.sep}{sound[1]}")


if __name__=="__main__":
    logging.error("This file isn't supposed to be executed!")
    exit()