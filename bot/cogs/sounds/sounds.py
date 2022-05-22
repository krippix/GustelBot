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
        self.SOUND_FOLDER = os.path.join(settings.DATA_FOLDER, "sounds")
        self.settings = settings
        self.settings.ensureFolder(self.SOUND_FOLDER)


    @commands.command(name="play", help="Play one of the bot's sound files.")
    async def play(self, ctx: commands.context, *args):
        logging.debug("<command> - play")
        
        # Check if channel is joinable at all
        if ctx.voice_client is not None:
            if ctx.author.voice.channel != ctx.voice_client.channel and not await voice.is_joinable(ctx, ctx.author.voice.channel):
                return
        
        # in case any arguments have been provided
        if args:
            sound = self.choose_sound(' '.join(args))

            if sound is None:
                await ctx.send("No sounds available.")
                return

            await ctx.send(f"Playing '{pathlib.Path(sound[1]).with_suffix('')}'")
            await voice.join_channel(ctx, ctx.author.voice.channel)
            await voice.play_sound(ctx, f"{sound[0]}{os.sep}{sound[1]}")
            return
        
        if ctx.author.voice is None:
            await ctx.send("Join a channel to use this command.")
            return
        
        sound = self.choose_sound()

        if sound is None:
            await ctx.send("No matching sound found.")
            return

        #print(f"{sound[0]}{sound[1]}")

        await voice.join_channel(ctx, ctx.author.voice.channel)
        await ctx.send(f"Playing '{pathlib.Path(sound[1]).with_suffix('')}'")
        await voice.play_sound(ctx, f"{sound[0]}{os.sep}{sound[1]}")


    @commands.command(name="stop", help="Stops playback")
    async def stop(self, ctx: commands.context, *args):
        
        if ctx.voice_client is None:
            await ctx.send("I am not connected to any channel.")
            return

        if not ctx.voice_client.is_playing():
            await ctx.send("There is nothing to stop")
            return

        ctx.voice_client.stop()



    @commands.command(name="disconnect", aliases=["dc","leave"], help="Disconnects bot from channel.")
    async def disconnect(self, ctx: commands.context):        
        # Disconnect bot from current channel
        logging.debug("<command> - disconnect")
        
        # This is kinda weird: ctx.voic_client is an object with type: voice_client.VoiceClient
        if ctx.voice_client is None:
            await ctx.send("I am not connected to any channel.")
            return
        
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()


    @commands.command(name="soundlist", aliases=["tree"], help="List available sounds.")
    async def soundlist(self, ctx: commands.context):
        # posts list of files in /sounds folder, without folder or extension.
        logging.debug("<command> - soundlist")
        
        reply_str = ""

        for file in filemgr.get_files_rec(self.SOUND_FOLDER):
            reply_str += f"{pathlib.Path(file[1]).with_suffix('')}\n"

        if len(reply_str) == 0:
            await ctx.send("No sounds found :sadge:")
            return

        await ctx.send(f"**The following songs are available:**\n{reply_str}")


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