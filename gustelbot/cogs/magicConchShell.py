# default
import logging
from pathlib import Path
import random
# pip
import discord
from discord.ext import commands
# internal
from gustelbot.util import config
from gustelbot.cogs import sounds


class MagicConchShell(commands.Cog):
    FOLDER_CONCH: Path

    possible_answers = []

    def __init__(self, bot, settings: config.Config):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.FOLDER_CONCH = Path(settings.folders['sounds_default'], 'magic_conch_shell')
        self.settings = settings

        self.prepare_answers()

    def prepare_answers(self):
        """
        Creates list of possible answers, associated with their soundfile
        """
        self.possible_answers = [
            (
                "Eines Tages vielleicht.",
                Path(self.FOLDER_CONCH, "einesTagesVielleicht.mp3")
            ),
            (
                "Nein.",
                Path(self.FOLDER_CONCH, "nein.mp3")),
            (
                "Nein!",
                Path(self.FOLDER_CONCH, "nein!.mp3")),
            (
                "Ich glaub' eher nicht.",
                Path(self.FOLDER_CONCH, "ichGlaubEherNicht.mp3")
            ),
            (
                "Ja.",
                Path(self.FOLDER_CONCH, "ja.mp3")
            ),
            (
                "Frag doch einfach nochmal.",
                Path(self.FOLDER_CONCH, "fragDochEinfachNochmal.mp3")
            )
        ]

    @discord.slash_command(name="conch", name_localizations={'de': 'muschel'}, description="Magic Conch Shell.")
    @discord.option(name="question", description="Yes or no question", default="", required=False)
    async def play(self, ctx: discord.ApplicationContext, question: str):
        result = random.choice(self.possible_answers)

        if await MagicConchShell.can_play(ctx):
            await sounds.Sounds.play_sound(ctx, result[1])
        if question:
            message = f"> {str(question)}\n{result[0]}"
        else:
            message = result[0]
        await ctx.respond(message)

    @staticmethod
    async def can_play(ctx: discord.ApplicationContext):
        """
        Ensures that the bot joining currently is reasonable. Following checks:
            - user is in a channel
            - bot is not in a channel OR bot is not playing anything at the moment
        """
        if ctx.author.voice is None:
            return False

        if ctx.voice_client is not None:
            if ctx.voice_client.is_playing():
                return False
        return True
