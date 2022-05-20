import logging
import discord
from discord.ext import commands

async def is_joinable(ctx: commands.context, channel: discord.VoiceChannel) -> bool:
    # Checks if voice channel can be joined, returns tuple (True/False, "reason")
    
    # Check if Channel is full
    if channel.user_limit != 0:
        if channel.user_limit == len(channel.members):
            await ctx.send("Channel is already full.")
            return False
    
    return True


async def join_channel(ctx: commands.context, channel: discord.VoiceChannel):
    '''join channel, this doesen't check if its possible!'''

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
    '''Play sound in current channel'''
    
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    ctx.voice_client.play(discord.FFmpegOpusAudio(sound))