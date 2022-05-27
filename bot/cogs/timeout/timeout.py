import logging, asyncio
import discord
from discord.ext import commands

class Timeout(commands.Cog):
    '''This class is supposed to handle bot timeouts. Currently only using voice_state as basis.'''

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        '''Handles automatic disconnection after 30s of inactivity. Only handles sending, not recording.'''
        logging.debug("<timeout> - voice state update")

        if not member.id == self.bot.user.id:
            return
        
        if after is None:
            return
        
        # disconnect once this variable reaches 30
        dc_timer = 0
        max_time = 180
        voiceClient = self.get_voice_client(after.channel)

        if voiceClient is None:
            return

        try:         
            while (self.bot.user in after.channel.members):
                await asyncio.sleep(1)
                dc_timer += 1
                logging.debug(f"Disconnect timer for {after.channel}, {max_time - dc_timer}s left.")

                if voiceClient.is_playing():
                    dc_timer = 0
                
                if dc_timer == max_time:
                    await voiceClient.disconnect()
                    return
        # this is called when bot has been disconnected
        except Exception as e:
            pass


    def get_voice_client(self, channel: discord.channel) -> discord.VoiceClient:
        '''Returns voice client, if bot is connected to the channel'''
        for client in self.bot.voice_clients:
            if client.channel == channel:
                return client
        
        return None
