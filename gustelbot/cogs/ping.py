# default
import logging
# pip
import discord
from discord.ext import commands
# internal
from gustelbot.util import config


class Ping(commands.Cog):

    def __init__(self, bot, settings: config.Config):
        self.logger = logging.getLogger(__name__)
        self.bot = bot

    @discord.slash_command(name="ping", description="Replies with bot's latency.")
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.respond(f"Latency: {int(self.bot.latency * 1000)}ms")
