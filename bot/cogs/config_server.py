# default
import logging
import traceback
# pip
import discord
from discord.ext import commands
# internal
from util import config
from util import database


class Config_Server(commands.Cog):
    """Allows configuration of server-side bot commands
    """
    db: database.Database

    def __init__(self, bot: commands.Bot, settings: config.Config, db: database.Database):
        self.logger = logging.getLogger(__name__)
        self.bot = bot
        self.db = db

    # command group
    config = discord.SlashCommandGroup("config", "configure this server")

    # config_group
    config_admin = config.create_subgroup("admin", "configure admin groups for this server")

    @config_admin.command(name="addgroup", description="allow group to edit bot config")
    @discord.option(name="group", description="Group to be registered as GustelBot admin")
    async def admin_addgroup(self, ctx: commands.Context, group: discord.Role):
        if not Config_Server.__is_allowed(ctx):
            await Config_Server.__permission_error(ctx)
            return
        try:
            result_code = self.db.add_admin_group(ctx.guild.id, group.name)
        except Exception:
            logging.error(f"Failed to add admin group: {traceback.format_exc()}")
            await ctx.respond("Internal Server Error")
            return
        if result_code == 409:
            await ctx.respond(f"{group.name} already registered as bot-admin.")
            return
        await ctx.respond(f"Added group {group.name} to bot-admins.")
        return

    @config_admin.command(name="remgroup", description="disallow group from editing bot config")
    @discord.option(name="group", description="Group to be removed from GustelBot admins")
    async def admin_delgroup(self, ctx: commands.Context, group: discord.Role):
        if not Config_Server.__is_allowed(ctx):
            await Config_Server.__permission_error(ctx)
            return
        try:
            result_code = self.db.remove_admin_group(ctx.guild.id, group.name)
        except Exception:
            logging.error(f"Failed to remove admin group: {traceback.format_exc()}")
            await ctx.respond("Internal Server Error")
            return
        if result_code == 404:
            await ctx.respond(f"Group {group.name} is not registered as bot-admin.")
            return
        await ctx.respond(f"Group {group.name} is no longer registered as bot-admin.")

    # command play group
    config_play = config.create_subgroup("play", "configure behaviour of play command")

    @config_play.command(name="maxlength", description="change maximum length when playing random sound.")
    @discord.option(name="seconds", min=0, max=1800, description="Maximum seconds allowed. Zero == unlimited")
    async def play_maxlength(
        self, ctx: commands.Context,
        seconds: int
    ):
        if not Config_Server.__is_allowed(ctx):
            await Config_Server.__permission_error(ctx)
            return
        try:
            self.db.set_play_maxlen(ctx.guild.id, seconds)
        except Exception:
            logging.error(f"Failed to set maxlength: {traceback.format_exc()}")
            await ctx.respond("Internal Server Error")
            return
        await ctx.respond(f"Max length of randomly chosen tracks set to {seconds} seconds.")
        return

    def __is_allowed(ctx: commands.Context):
        # Checks if access to command was justified
        if ctx.author == ctx.guild.owner:
            return True

    async def __permission_error(ctx: commands.Context):
        await ctx.respond("You are not allowed to change server settings.")
        return
