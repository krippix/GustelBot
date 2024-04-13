# default
import logging
import traceback
# pip
import discord
from discord.ext import commands
from discord.ext import tasks
# internal
from util import config
from util import database


# Set loglevel, ignoring config until config file works
logging.basicConfig(encoding='utf-8', level=10)

# Check config file for errors and correct them
settings = config.Config()
try:
    db = database.Database()
except Exception:
    db = None
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
    db.add_server(server_id=guild.id, name=guild.name)


@bot.event
async def on_guild_update(_, guild: discord.Guild):
    logging.info(f"Guild {guild.name} was updated")
    db.add_server(server_id=guild.id, name=guild.name)


@tasks.loop(hours=1)
async def check_guilds():
    """
    Checks if all guilds are part of the database and data is up-to-date
    """
    discord_guilds = [guild async for guild in bot.fetch_guilds()]
    for guild in discord_guilds:
        if (srv := db.get_server(server_id=guild.id)) is not None:
            if srv['servername'] == guild.name:
                continue
        db.add_server(server_id=guild.id, name=guild.name)


def load_extensions(bot):
    """
    Loads extensions for bot. Manual cogs have to be imported as well.
    """
    logging.info("Loading Extensions.")

    # Regular cogs
    from cogs import magischeMiesmuschel
    from cogs import ping
    from cogs import timeout
    manual_cogs = {
        'magischeMiesmuschel': magischeMiesmuschel.MagischeMiesmuschel,
        'ping': ping.Ping,
        'timeout': timeout.Timeout
    }

    # cogs using database and config
    from cogs import brotato
    from cogs import config_server
    from cogs import sounds
    manual_cogs_db = {
        'brotato': brotato.Brotato,
        'config_server': config_server.Config_Server,
        'sounds': sounds.Sounds
    }
    for cog in manual_cogs:
        try:
            logging.debug(f"Attempting to import {cog}")
            bot.add_cog(manual_cogs[cog](bot, settings))
            logging.info(f"Loaded Module {cog}.")
        except Exception as e:
            logging.error(f"Failed to load '{cog}': {e}")

    for cog in manual_cogs_db:
        try:
            logging.debug(f"Attempting to import {cog}")
            bot.add_cog(manual_cogs_db[cog](bot, settings, db))
            logging.info(f"Loaded Module {cog}.")
        except Exception as e:
            logging.error(f"Failed to load '{cog}': {type(e)}")
    logging.info("Finished loading Modules.")


# Launch Bot
if __name__ == "__main__":
    try:
        load_extensions(bot)
        bot.run(settings.get_discord_token())
    except Exception:
        logging.critical(f"Failed to start bot: {traceback.format_exc()}")
        exit()
