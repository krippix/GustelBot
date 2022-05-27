import logging

import discord
from discord.ext import commands

class Ping(commands.Cog):

    def __init__(self, bot: commands.Bot):
        logging.debug("<ping> - __init__")
        self.bot = bot

    @discord.slash_command(name="ping", description="Replies with bot's latency.")
    async def ping(self, ctx: commands.context):
        await ctx.respond(f"Latency: {int(self.bot.latency * 1000)}ms")
        return