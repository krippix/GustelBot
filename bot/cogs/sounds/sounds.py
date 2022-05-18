import logging
import os
import pathlib
from discord.ext import commands
from util import config, filemgr

class Sounds(commands.Cog):
    SOUND_FOLDER: pathlib.Path

    def __init__(self, bot):
        self.bot = bot
        self.SOUND_FOLDER = os.path.join(config.Config().DATA_FOLDER, "sounds")
        config.Config().ensureFolder(self.SOUND_FOLDER)

    @commands.command(name="play", help="Play one of the bot's sound files.")
    async def ping(self, ctx: commands.context, *args):
        
        if not args:
            await self.playSound(ctx)
            return
        
        await ctx.send("Jetzt würde dein Parameter gesucht und abgespielt werden.")


    @commands.command(name="soundlist", help="List available sounds.")
    async def soundlist(self, ctx: commands.context):
        # posts list of files in /sounds folder, without folder or extension.
        reply_str = ""

        for file in filemgr.get_files_rec(self.SOUND_FOLDER):
            reply_str += f"{pathlib.Path(file[1]).with_suffix('')}\n"

        if len(reply_str) == 0:
            await ctx.send("No sounds found :sadge:")
            return

        await ctx.send(f"**The following songs are available:**\n{reply_str}")


    async def playSound(self, ctx: commands.context, name = None):
        # Plays random sound if no name is given

        if ctx.author.voice is None:
            await ctx.send("Join a channel to use this command.")
            return

        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()

        await ctx.author.voice.channel.connect()

        TODO CONTINUE HERE

        await ctx.send(filemgr.get_random_file(self.SOUND_FOLDER))


