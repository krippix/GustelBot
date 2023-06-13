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
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.settings = settings
        self.database = database

    # command group
    brotato = discord.SlashCommandGroup("brotato", "Collection of brotato commands")

    @brotato.command(name="top5", description="returns 5 runs with highes wave")
    async def top5(self, ctx: commands.Context):
        pass

    @brotato.command(name="highscore", description="highest run per character")
    async def highscore(self, ctx: commands.Context, difficulty: discord.Option(int, min_value=0, max_value=5, required=False)):
        result = self.__format_result(self.database.get_brotato_highscore(difficulty))
        await ctx.respond(result)

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
            print(chars)
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

    def __format_result(self, result: list[tuple]):
        """Formats highscore table
        Expected tuples: (username,wave,danger,char_name)
        """

        if result is None or len(result) == 0:
            return "No highscores found."

        # define max width of each column
        result_list = [["Spieler","Welle","Gefahr","Charakter"]]
        max_width = [0,0,0,0]

        # convert tuples to lists
        for tuple in result:
            result_list.append(list(tuple))

        # cast each column to string and determine max width
        for curr_list in result_list:
            for x in range(0,4):
                curr_list[x] = str(curr_list[x])
                if len(curr_list[x]) > max_width[x]:
                    max_width[x] = len(curr_list[x])
        # append spacebars to reach max_length on each item
        result_string = "Aktuelle Highscores:\n```"
        for curr_list in result_list:
            for x in range(0,4):
                result_string = f"{result_string}{curr_list[x]} {(max_width[x] - len(curr_list[x])) * ' '}"
            result_string += "\n"
        return result_string + "```"