import logging, pathlib, os, random
from difflib import SequenceMatcher
import discord
from discord.ext import commands
from util import config, filemgr, voice

class MagischeMiesmuschel(commands.Cog):
    FOLDER_MUSCHEL: pathlib.Path
    
    possible_answers = []

    def __init__(self, bot, settings: config.Config):
        logging.debug("<init> - sounds")

        self.bot = bot
        self.FOLDER_MUSCHEL = os.path.join(settings.folders["sounds_default"], "miesMuschel")
        self.settings = settings
        self.settings.ensureFolder(self.FOLDER_MUSCHEL)

        self.prepare_answers()


    def prepare_answers(self):
        '''Creates List containing Tuples of the format ("Answer", file)'''
        self.possible_answers = [
            ("Eines Tages vielleicht.",os.path.join(self.FOLDER_MUSCHEL, "einesTagesVielleicht.mp3")),
            ("Nein.", os.path.join(self.FOLDER_MUSCHEL, "nein.mp3")),
            ("Nein!", os.path.join(self.FOLDER_MUSCHEL, "nein!.mp3")),
            #("Garnichts.", os.path.join(self.FOLDER_MUSCHEL, "garnichts.mp3")),
            #("Keins von beiden.",""),
            ("Ich glaub' eher nicht.", os.path.join(self.FOLDER_MUSCHEL, "ichGlaubEherNicht.mp3")),
            ("Ja.", os.path.join(self.FOLDER_MUSCHEL, "ja.mp3")),
            ("Frag doch einfach nochmal.", os.path.join(self.FOLDER_MUSCHEL, "fragDochEinfachNochmal.mp3"))
        ]


    @discord.slash_command(name="muschel", description="Magische Miesmuschel.")
    async def play(self, ctx: discord.ApplicationContext, question: discord.Option(str, "Question that can be answered with yes/no", default="", name="question")):
        logging.debug("<MagischeMiesmuschel>")
        
        result = random.choice(self.possible_answers)
        
        await ctx.respond(result[0])

        if ctx.voice_client is None:
            await voice.join_channel(ctx, ctx.author.voice.channel)
        else:
            # Check if bot is already in use
            if ctx.voice_client.is_playing():
                return
            # Check if channel is joinable at all
            if ctx.author.voice.channel != ctx.voice_client.channel and not await voice.is_joinable(ctx, ctx.author.voice.channel):
                return
            if ctx.author.voice.channel != ctx.voice_client.channel:
                await voice.join_channel(ctx, ctx.author.voice.channel)

        
        print("Playing: ", result[1])
        await voice.play_sound(ctx, result[1])
        return