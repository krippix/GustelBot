# default
import logging
# pip
import discord
from discord.ext import commands
# internal
from gustelbot.util import config
from gustelbot.util.database import Brotato as BrotatoCon
from gustelbot.util.database import Database
from gustelbot.util.database import User


class Brotato(commands.Cog):
    """
    Class used for tracking brotato highscores
    """

    bot: commands.Bot
    settings: config.Config

    def __init__(self, bot: commands.Bot, settings: config.Config):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.settings = settings

    # command group
    brotato = discord.SlashCommandGroup("brotato", "Collection of brotato commands")

    @brotato.command(name="highscore", description="Shows 20 best runs")
    @discord.option(name="difficulty", description="Difficulty to show", min_value=0, max_value=5, required=False)
    @discord.option(name="character", description="Name of Character who's runs to show", required=False)
    async def highscore(self, ctx: discord.ApplicationContext, difficulty: int, character: str):
        """Displays highscores of the current server.

        Args:
            ctx: _description_
            difficulty: _description_. Defaults to 0, max_value=5, required=False).
            character: _description_. Defaults to False).
        """
        self.__ensure_server(ctx)
        db_con = Database.new_connection()

        result = BrotatoCon.get_brotato_highscore(db_con, difficulty, character, ctx.guild.id)
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
        self, ctx: discord.ApplicationContext,
        char: str,
        wave: int,
        danger: int,
        user: discord.Member
    ):
        if user is None:
            user = ctx.author

        self.__ensure_server(ctx)
        self.__ensure_user(ctx, user)
        db_con = Database.new_connection()

        chars = [str(x["name_de"]).lower() for x in BrotatoCon.get_brotato_char(db_con)]

        if str(char).lower() not in chars:
            await ctx.respond(f"'{char}' is an unknown character")
            return

        BrotatoCon.add_brotato_run(db_con, char, wave, danger, user.id, ctx.guild.id)
        db_con.commit()
        await ctx.respond(f"**Run hinzugefügt:**\nCharakter: `{char}`, Welle: `{wave}`, Gefahr: `{danger}`")

    @brotato_add.command(name="char", description="add character")
    @discord.option(name="char", description="Character to add")
    async def add_char(self, ctx: discord.ApplicationContext, char: str):
        db_con = Database.new_connection()

        db_char = Brotato.get_brotato_char(db_con, char)
        if db_char is None:
            Brotato.add_brotato_char(db_con, char)
            await ctx.respond(f"Added new char '{char}'")
            db_con.commit()
        else:
            await ctx.respond(f"Character '{char}' already exists.")

    # remove subgroup
    brotato_rem = brotato.create_subgroup(name="remove", description="remove")

    # helper functions
    @staticmethod
    def __ensure_server(ctx: discord.ApplicationContext):
        """Makes sure the context server is part of the database
        Args:
            ctx: command context
        """
        db_con = Database.new_connection()
        if ctx.guild is None:
            return
        Database.add_server(db_con, ctx.guild.id, ctx.guild.name)
        db_con.commit()

    @staticmethod
    def __ensure_user(ctx: discord.ApplicationContext, user: discord.Member):
        """Makes sure mentioned user is part of the database
        Args:
            ctx: _description_
            user: _description_
        """
        db_con = Database.new_connection()
        User.add_user(db_con, user.id, user.name)
        User.add_user_display_name(db_con, user.id, ctx.guild.id, user.display_name)
        db_con.commit()

    @staticmethod
    def __format_table(lst: list[tuple], header: list) -> str:
        """Formats input list and header into a table using monospace.

        Args:
            header: Head row
            lst: content to format

        Returns:
            str: result string
        """
        if lst is None or len(lst) == 0:
            return ""

        # define max width of each column
        result_list = [header]
        max_width = [0] * len(header)

        # convert tuples to lists
        for row in lst:
            result_list.append(list(row))

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
