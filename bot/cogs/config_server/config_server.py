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
    async def admin_addgroup(self, ctx: commands.Context, group: discord.Option(discord.Role)):
        if not Config_Server.__is_allowed(ctx):
            Config_Server.__permission_error(ctx)
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
    async def admin_delgroup(self, ctx: commands.Context, group: discord.Option(discord.Role)):
        if not Config_Server.__is_allowed(ctx):
            Config_Server.__permission_error(ctx)
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

    def __is_allowed(ctx: commands.Context):
        # Checks if access to command was justified
        if ctx.author == ctx.guild.owner:
            return True
    
    async def __permission_error(ctx: commands.Context):
        await ctx.respond("You are not allowed to change server settings.")
        return
        