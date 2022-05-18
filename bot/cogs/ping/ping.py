import logging
from discord.ext import commands
from util import config

class Ping(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", help="Ping bot, replies with pong")
    async def ping(self, ctx: commands.context, *args):
        await ctx.send("pong")
        return