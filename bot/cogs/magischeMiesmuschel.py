# default
import logging
import pathlib
import os
import random
# pip
import discord
from discord.ext import commands
# internal
from util import config
from util import voice


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
            ("Eines Tages vielleicht.", os.path.join(self.FOLDER_MUSCHEL, "einesTagesVielleicht.mp3")),
            ("Nein.", os.path.join(self.FOLDER_MUSCHEL, "nein.mp3")),
            ("Nein!", os.path.join(self.FOLDER_MUSCHEL, "nein!.mp3")),
            ("Ich glaub' eher nicht.", os.path.join(self.FOLDER_MUSCHEL, "ichGlaubEherNicht.mp3")),
            ("Ja.", os.path.join(self.FOLDER_MUSCHEL, "ja.mp3")),
            ("Frag doch einfach nochmal.", os.path.join(self.FOLDER_MUSCHEL, "fragDochEinfachNochmal.mp3"))
        ]

    @discord.slash_command(name="muschel", description="Magische Miesmuschel.")
    @discord.option(name="question", description="Yes or no question", default="", required=False)
    async def play(self, ctx: discord.ApplicationContext, question: str):
        result = random.choice(self.possible_answers)

        await ctx.respond(f"> {str(question)}\n{result[0]}")

        # Check if channel is joinable at all
        if not await voice.is_joinable(ctx, ctx.author.voice.channel):
            return
        if ctx.author.voice.channel != ctx.voice_client.channel:
            await voice.join_channel(ctx, ctx.author.voice.channel)

        print("Playing: ", result[1])
        await voice.play_sound(ctx, result[1])
        return

    async def can_join(ctx: discord.ApplicationContext):
        '''
        Ensures that the bot joining currently is reasonable. Following checks:
            - user is in a channel
            - bot is not in a channel OR bot is not playing anything at the moment
        '''
        if ctx.author.voice is None:
            return False

        if ctx.voice_client is not None:
            if ctx.voice_client.is_playing():
                return False

        return True
