# default
import logging
# pip
import discord
from discord.ext import commands
# internal


async def is_joinable(ctx: commands.Context) -> tuple[bool, str | None]:
    """
    Checks if bot can join the channel of the context author
    """
    if ctx.author.voice is None:
        return False, "You are not in a voice channel!"

    if not ctx.author.voice.channel.user_limit:
        return True, None

    if ctx.author.voice.channel.user_limit == len(ctx.author.voice.channel.members):
        return False, "Channel is already full!"


async def join_channel(ctx: commands.context, channel: discord.VoiceChannel):
    '''Joins channel, this doesen't check if its possible!'''

    # if bot is already in a channel, disconnect
    if ctx.voice_client is not None:
        if ctx.voice_client.channel == channel:
            return
        await ctx.voice_client.disconnect()

    try:
        await channel.connect()
    except Exception as e:
        await ctx.send("Failed to join your channel.")
        logging.error(f"Failed to join channel {ctx.author.voice}: {e}")
        raise e


async def play_sound(ctx: commands.context, sound):
    '''Plays sound in current channel'''
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    # options is used for EBU R128
    ctx.voice_client.play(discord.FFmpegOpusAudio(sound, options="-filter:a loudnorm"))
