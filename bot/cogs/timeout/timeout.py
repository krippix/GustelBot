import logging, asyncio, os, time
import discord
from discord.ext import commands
from util import voice, config

class Timeout(commands.Cog):
    '''This class is supposed to handle bot timeouts. Currently only using voice_state as basis.'''

    def __init__(self, bot, settings: config.Config):
        self.bot = bot


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        '''Handles automatic disconnection after max_time seconds of inactivity. Only handles sending, not recording.'''
        logging.debug("<timeout> - voice state update")

        if not member.id == self.bot.user.id:
            return
        
        if after is None:
            return
        
        # disconnect once this variable reaches max_time
        dc_timer = 0
        max_time = 180
        voice_client = self.get_voice_client(after.channel)

        if voice_client is None:
            return

        try:         
            while (self.bot.user in after.channel.members):
                await asyncio.sleep(1)
                dc_timer += 1
                logging.debug(f"Disconnect timer for {after.channel}, {max_time - dc_timer}s left.")

                if voice_client.is_playing():
                    dc_timer = 0
                
                if dc_timer >= max_time:
                    voice_client.play(discord.FFmpegOpusAudio(os.path.join(config.Config().folders["sounds_default"],"timeout.wav")),)
                    while voice_client.is_playing():
                        time.sleep(1)                
                    await voice_client.disconnect()
                    return
        # this is called when bot has been disconnected
        except Exception as e:
            print(e)
            pass


    def get_voice_client(self, channel: discord.channel) -> discord.VoiceClient:
        '''Returns voice client, if bot is connected to the channel'''
        for client in self.bot.voice_clients:
            if client.channel == channel:
                return client
        
        return None
