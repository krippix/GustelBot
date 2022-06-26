import logging, pathlib, os, random
from difflib import SequenceMatcher
import discord
from discord.ext import commands
from util import config, filemgr, voice

class MagischeMiesmuschel(commands.Cog):
    SOUND_FOLDER: pathlib.Path
    
    possible_answers = [
        ("Eines Tages vielleicht.",""),
        ("Nein.","normal"),
        ("Nein.","genervt"),
        ("Nein.","nochmal normal"),
        ("Garnichts.",""),
        ("Keins von beiden.",""),
        ("Ich glaub' eher nicht.",""),
        ("Ja.",""),
        ("Frag doch einfach nochmal.","")
    ]

    def __init__(self, bot, settings: config.Config):
        logging.debug("<init> - sounds")

        self.bot = bot
        self.SOUND_FOLDER = os.path.join(settings.DATA_FOLDER, "sounds")
        self.settings = settings
        self.settings.ensureFolder(self.SOUND_FOLDER)


    @discord.slash_command(name="muschel", description="Magische Miesmuschel.")
    async def play(self, ctx: discord.ApplicationContext):
        logging.debug("<MagischeMiesmuschel>")
        
        result = random.choice(self.possible_answers)
        
        await ctx.respond(result[0])

        # Check if channel is joinable at all
        if ctx.voice_client is not None:
            if ctx.author.voice.channel != ctx.voice_client.channel and not await voice.is_joinable(ctx, ctx.author.voice.channel):
                return
        
        # in case any arguments have been provided

        sound = self.choose_sound(result[1])

        await self.play_sound(ctx, sound)
        return


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