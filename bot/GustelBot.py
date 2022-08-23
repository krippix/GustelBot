import logging
import os
import discord
from discord.ext import commands
from util import config


# Set loglevel, ignoring config until config file works
logging.basicConfig(encoding='utf-8', level=10)

# Check config file for errors and correct them
settings = config.Config()
# overwrite loglevel
logging.basicConfig(level=settings.get_loglevel(), force=True)

# specify intents (permission stuff)
intents = discord.Intents.default()

# Create bot object
bot = commands.Bot(case_insensitive=True, intents=intents, debug_guilds=[settings.get_config("CLIENT","debug_guild")])


@bot.event
async def on_ready():
    logging.info(f"Successfully logged in as {bot.user}")
    
    logging.info("Setting status.")
    # await bot.change_presence(activity=discord.Game(name="["+settings.get_bot_prefix()+"]"))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Alexander Marcus"))


def load_extensions(bot):
    '''Loads extensions for bot. Manual cogs have to be imported as well.'''
    logging.info("Loading Extensions.")

    # Manually imported cogs. To pass more variables.
    from cogs.sounds import sounds
    from cogs.magischeMiesmuschel import magischeMiesmuschel
    manual_cogs = {
        'sounds': sounds.Sounds,
        'magischeMiesmuschel' : magischeMiesmuschel.MagischeMiesmuschel
    }
    
    for cog in manual_cogs:
        try:
            logging.debug(f"Attempting to import {cog}")
            bot.add_cog(manual_cogs[cog](bot, settings))
            logging.info(f"Loaded Module {cog}.")
        except Exception as e:
            logging.error(f"Failed to load '{cog}': {e}")


    # Load left-over Modules from the cogs folder
    for cog in os.listdir(os.path.join(settings.folders["root"], "bot", "cogs")):
        if cog == "__pycache__":
            continue
        try:
            bot.load_extension(f"cogs.{cog}")
            logging.info(f"Loaded Module {cog}.")
        except discord.errors.NoEntryPointError:
            pass        
        except Exception as e:
            print(type(e))
            logging.error(f"Failed to load module {cog}: {e} Continuing")
    logging.info("Finished loading Modules.")


# Launch Bot
if __name__ == "__main__":
    try:
        load_extensions(bot)
        bot.run(settings.get_config("AUTH","discord_token"))
    except Exception as e:
        logging.critical(f"Failed to start bot: {e}")
        exit()