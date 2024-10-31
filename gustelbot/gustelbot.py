"""
Main entry point for GustelBot
"""
# default
import logging
import traceback
import datetime

# pip
import discord
from discord.ext import commands
from discord.ext import tasks
# internal
from gustelbot.util import config
from gustelbot.util.database import Database
from gustelbot.util.database import User


# Set loglevel, ignoring config until config file works
logging.basicConfig(encoding='utf-8', level=10)

# Check config file for errors and correct them
settings = config.Config()
try:
    db_con = Database.new_connection()
    Database.check(db_con)
    db_con.commit()
except Exception:
    logging.critical(traceback.format_exc())
    exit()

# overwrite loglevel
logging.basicConfig(level=settings.get_loglevel(), force=True)

# specify intents (permission stuff)
intents = discord.Intents.default()

# Create bot object
bot = commands.Bot(case_insensitive=True, intents=intents, debug_guilds=settings.get_debug_guilds())


# ----- database maintenance
@bot.event
async def on_ready():
    logging.info(f"Successfully logged in as {bot.user}")

    logging.info("Setting status.")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Alexander Marcus"))
    check_guilds.start()


@bot.event
async def on_guild_join(guild: discord.Guild):
    logging.info(f"Joined {guild.name}")
    Database.add_server(db_con, server_id=guild.id, name=guild.name)


@bot.event
async def on_guild_update(_, guild: discord.Guild):
    logging.info(f"Guild {guild.name} was updated")
    Database.add_server(db_con, server_id=guild.id, name=guild.name)


@tasks.loop(hours=1)
async def check_guilds():
    """
    Checks if all guilds are part of the database and data is up-to-date
    """
    discord_guilds = [guild async for guild in bot.fetch_guilds()]
    for guild in discord_guilds:
        if (srv := Database.get_server(db_con, server_id=guild.id)) is not None:
            if srv['servername'] == guild.name:
                continue
        Database.add_server(db_con, server_id=guild.id, name=guild.name)
    db_con.commit()


@bot.before_invoke
async def ensure_user(ctx: commands.Context | discord.ApplicationContext):
    """
    Ensures that the calling user is in the database.
    """
    logging.debug("Attempting to create user %s", ctx.author.name)
    User.add_user(db_con, ctx.author.id, ctx.author.name)
    User.add_user_display_name(db_con, ctx.author.id, ctx.guild_id, ctx.author.display_name)
    db_con.commit()


def load_extensions():
    """
    Loads extensions for bot. Manual cogs have to be imported as well.
    """
    logging.info("Loading Extensions.")

    # Regular cogs
    from gustelbot.cogs import ping
    from gustelbot.cogs import sounds
    from gustelbot.cogs import timeout
    from gustelbot.cogs import magicConchShell
    from gustelbot.cogs import brotato
    from gustelbot.cogs import config_server

    manual_cogs = {
        'ping': ping.Ping,
        'sounds': sounds.Sounds,
        'timeout': timeout.Timeout,
        'magic_conch_shell': magicConchShell.MagicConchShell,
        'brotato': brotato.Brotato,
        'config_server': config_server.ConfigServer,
    }

    for cog in manual_cogs:
        try:
            logging.debug(f"Attempting to import {cog}")
            bot.add_cog(manual_cogs[cog](bot, settings))
            logging.info(f"Loaded Module {cog}.")
        except Exception:
            logging.error(f"Failed to load '{cog}': {traceback.format_exc()}")
    logging.info("Finished loading Modules.")


# Launch Bot
def start():
    try:
        load_extensions()
        bot.run(settings.get_discord_token())
    except Exception:
        logging.critical(f"Failed to start bot: {traceback.format_exc()}")
        exit()
