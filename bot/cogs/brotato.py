# default
import logging
# pip
import discord
from discord.ext import commands
# internal
from util import config, database


class Brotato(commands.Cog):
    """Class used for tracking brotato highscores
    """

    bot: commands.Bot
    db: database.Database
    settings: config.Config

    def __init__(self, bot: commands.Bot, settings: config.Config, db: database.Database):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.settings = settings
        self.db = db

    # command group
    brotato = discord.SlashCommandGroup("brotato", "Collection of brotato commands")

    @brotato.command(name="highscore", description="Shows 20 best runs")
    @discord.option(name="difficulty", description="Difficulty to show", min_value=0, max_value=5, required=False)
    @discord.option(name="character", description="Name of Character who's runs to show", required=False)
    async def highscore(self, ctx: commands.Context, difficulty: int, character: str):
        """Displays highscores of the current server.

        Args:
            ctx: _description_
            difficulty: _description_. Defaults to 0, max_value=5, required=False).
            character: _description_. Defaults to False).
        """
        self.__ensure_server(ctx)

        result = self.db.get_brotato_highscore(difficulty, character, ctx.guild.id)
        result_table = self.__format_table(result[0], result[1])

        if result_table is None:
            result_table = "```\nNichts passendes gefunden\n```"

        if difficulty is None:
            difficulty = "alle"

        if character is None:
            character = "alle"

        msg = f"Gefahr: `{difficulty}`, Charakter: `{character}`"

        await ctx.respond(msg+"\n"+result_table)

    # add subgroup
    brotato_add = brotato.create_subgroup("add", "add")

    @brotato_add.command(name="run", description="add run to database")
    @discord.option(name="character", description="character used")
    @discord.option(name="wave", description="Highes wave reached", min_value=1)
    @discord.option(name="danger", description="Danger level of played run")
    @discord.option(name="user", description="User who achieved that run (optional)", required=False)
    async def add_run(
        self, ctx: commands.Context,
        char: str,
        wave: int,
        danger: int,
        user: discord.Member
    ):
        if user is None:
            user = ctx.author

        self.__ensure_server(ctx)
        self.__ensure_user(ctx, user)

        chars = [str(x["name_de"]).lower() for x in self.db.get_brotato_char()]

        if str(char).lower() not in chars:
            await ctx.respond(f"'{char}' is an unknown character")
            return

        self.db.add_brotato_run(char, wave, danger, user.id, ctx.guild.id)
        await ctx.respond(f"**Run hinzugefügt:**\nCharakter: `{char}`, Welle: `{wave}`, Gefahr: `{danger}`")

    @brotato_add.command(name="char", description="add character")
    @discord.option(name="character", description="Character to add")
    async def add_char(self, ctx: commands.Context, char: str):
        db_char = self.db.get_brotato_char(char)
        if db_char is None:
            self.db.add_brotato_char(char)
            await ctx.respond(f"Added new char '{char}'")
            return
        await ctx.respond(f"Character '{char}' already exists.")

    # remove subgroup
    botato_rem = brotato.create_subgroup("remove", "remove")

    # helper functions
    def __ensure_server(self, ctx: commands.Context):
        """Makes sure the context server is part of the database
        Args:
            ctx: command context
        """
        if ctx.guild is None:
            return
        self.db.add_server(ctx.guild.id, ctx.guild.name)

    def __ensure_user(self, ctx: commands.Context, user: discord.Member):
        """Makes sure mentioned user is part of the database
        Args:
            ctx: _description_
            user: _description_
        """
        self.db.add_user(user.id, user.name)
        self.db.add_user_displayname(user.id, ctx.guild.id, user.display_name)

    def __format_table(self, lst: list[tuple], header: list) -> str:
        """Formats input list and header into a table using monospace.

        Args:
            header: Head row
            lst: content to format

        Returns:
            str: result string
        """
        if lst is None or len(lst) == 0:
            return None

        # define max width of each column
        result_list = [header]
        max_width = [0] * len(header)

        # convert tuples to lists
        for tuple in lst:
            result_list.append(list(tuple))

        # cast each column to string and determine max width
        for curr_list in result_list:
            for x in range(0, len(header)):
                curr_list[x] = str(curr_list[x])
                if len(curr_list[x]) > max_width[x]:
                    max_width[x] = len(curr_list[x])
        # append spacebars to reach max_length on each item
        result_string = "```"
        for curr_list in result_list:
            for x in range(0, len(header)):
                result_string = f"{result_string}{curr_list[x]} {(max_width[x] - len(curr_list[x])) * ' '}"
            result_string += "\n"
        return result_string + "```"
