# python native
import logging
# external
import discord
from discord import utils
from discord.ext import commands
# project
from util import config, database

class Brotato(commands.Cog):
    """Class used for tracking brotato highscores
    """

    def __init__(self, bot: commands.Bot, settings: config.Config, database: database.Database):
        self.bot = bot
        self.settings = settings
        self.database = database

    # command group
    brotato = discord.SlashCommandGroup("brotato", "Collection of brotato commands")

    @brotato.command(name="list", description="displays current highscores")
    async def wasistdas(self, ctx):
        await ctx.respond("Aaron ist letzter!")
    
    # add subgroup
    brotato_add = brotato.create_subgroup("add", "add")

    @brotato_add.command(name="run", description="add run to database")
    async def add_run(
        self, ctx: commands.Context, 
        char: discord.Option(str),
        wave: discord.Option(int, min_value=1),
        danger: discord.Option(int),
        user: discord.Option(discord.Member, required=False)
    ):
        if user is None:
            user = ctx.author

        chars = [x.lower() for x in self.database.get_brotato_char_all()]

        if char.lower() not in chars:
            logging.debug(chars)
            await ctx.respond(f"'{char}' is an unknown character")
            return
        
        if self.database.get_user(user.id) is None:
            self.database.add_user(user.id, user.nick)

        self.database.add_brotato_run(char,wave,danger,user.id,ctx.guild.id) 
        await ctx.respond(f"Run hinzugefügt.")

    @brotato_add.command(name="char", description="add character")
    async def add_char(self, ctx: commands.Context, char: discord.Option(str)):
        db_char = self.database.get_brotato_char(char)
        if db_char is None:
            self.database.add_brotato_char(char)
            await ctx.respond(f"Added new char '{char}'")
            return
        await ctx.respond(f"Character '{char}' already exists.")
        

    # remove subgroup
    botato_rem = brotato.create_subgroup("remove", "remove")


