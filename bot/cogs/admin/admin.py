import logging, os, sys
import discord
from discord.ext import commands
from util import config

class Admin(commands.Cog):
    
    def __init__(self, bot, settings: config.Config):
        self.bot = bot
        self.settings = settings

    @commands.command(name="prefix", help="Change Bot Prefix.")
    async def ping(self, ctx: commands.context, *args):
        #print(ctx.message.author.guild_permissions.administrator)
        
        if (not check_permissions(ctx.message.author)):
            await ctx.send("You do not fulfill the required permissions to use this command.")
            return

        if len(args) < 1:
            await ctx.send("Missing argument")
            return

        try:
            self.settings.set_config("CLIENT","prefix",args[0])
        except Exception as e:
            await ctx.send("Failed to write new prefix to config!")

        try:
            self.bot.command_prefix = args[0]
            await ctx.send("Prefix has been set to "+args[0])
        except Exception as e:
            await ctx.send("Failed to set new prefix")

        await self.bot.change_presence(activity=discord.Game(name="["+self.settings.get_bot_prefix()+"]"))

"""  
    @commands.command(name="reload", help="Restarts the bot")
    async def ping(self, ctx: commands.context, *args):
        if not ctx.message.author.id == bot.owner_id:
            await ctx.send("This command can currently only be used by the bot author")
            return

        await ctx.message.add_reaction("✅")
        restart_self()
""" 

def check_permissions(author):
    # Checks if user has any admin-permissions
    # This is ugly but I don't know if there is a proper way to iterate over permissions

    # List of permissions that allow bot management
    logging.debug("Author Roles: "+str(author.roles))
    
    for role in author.roles:
        if str(role).lower() == "bot-admin": 
            logging.debug("User is member of 'bot-admin'")
            return True
     
    if author.guild_permissions.administrator:
        return True
    
    if author.guild_permissions.manage_channels:
        return True

    return False


def restart_self():
    os.execv(sys.argv[0], sys.argv)