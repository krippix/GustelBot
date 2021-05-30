#Python "native"
import logging
from pathlib import Path
import os
import random

#Part of Project
import config
import commands_play
import commands_reddit
import commands_youtube
import GustelBOT

#external
import discord
from discord.ext import commands
from discord import message

logging.getLogger().setLevel(logging.INFO)

def main():
    #Check requirements / create missing files
    config.checkLocations()
    
    # Returns True if config existed
    if not config.checkini():
        logging.error("config.ini didn't exist. Please enter your Discord Token.")
        logging.warning("Exiting GustelBOT...")
        exit()
        
    

    #Setting the bot prefix
    try:
        prefix = config.readini( "BOTCONFIG", "prefix")
        
        if prefix == None:
            logging.error("No Prefix defined! Falling back to '&'")
            bot = commands.Bot(command_prefix=('&'),case_insensitive=True)
        else:
            bot = commands.Bot(command_prefix=(prefix),case_insensitive=True)
            logging.info("Prefix set to: "+prefix)
    except Exception as e:
        logging.error("Failed to read prefix: "+str(e))
        loggging.info("Falling back to prefix '&'")
    
    
    
    #INFO once bot is connected and ready
    @bot.event
    async def on_ready():
        logging.info('Logged in as {0.user}'.format(bot))
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Alexander Marcus"))
    
    
    
    #BOT actions when recieving message
    @bot.event
    async def on_message(message):
        
        #exclude messages by BOT itself
        if message.author == bot.user:
            return
        logging.info(str(message.author)+": "+str(message.content))
        await bot.process_commands(message)
        
    #when last user leaves channel
    #@bot.event
    #async def on_
        
        
        
    #--------------
    #Commands
    #--------------
    
    @bot.command(pass_context=True,name="join",description="BOT tritt dem Channel bei")
    async def cmdJoin(ctx):
        
        userchannel = ctx.author.voice
        
        if userchannel == None:
            await ctx.send("You have to be in a voice channel to use this command!")
            return
        
        else:
            vc = await userchannel.channel.connect()
            await ctx.send("Joining '"+ str(userchannel.channel)+"'.")
            #vc.play(discord.FFmpegPCMAudio(os.path.join("FreshD\\eyyyy.wav")))
            #while vc.is_playing():
                
    @bot.command(pass_context=True,name="tree",description="Lists all available soundfiles")
    async def cmdJoin(ctx):
        
        await ctx.send(commands_play.tree())
    
    
    
    @bot.command(pass_context=True,name="disconnect",aliases=["leave","exit"],description="BOT leaves channel.")
    async def cmdLeave(ctx):
 
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected.")
    
    
    
    @bot.command(pass_context=True, name="play",aliases=["paly"], description="BOT plays sound")
    async def cmdPlay(ctx, *args):
        
        #If neither bot nor author are in a channel
        if ctx.voice_client is None and ctx.author.voice is None:
            await ctx.send("You have to join a channel to use this command!")
            return
        
        #If bot is in no channel yet, join author
        elif ctx.voice_client is None and ctx.author.voice is not None:
            await ctx.author.voice.channel.connect()
        
        #If bot is in the wrong channel, switch to author
        elif ctx.voice_client.channel != ctx.author.voice.channel:
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            await ctx.author.voice.channel.connect()
        
        #If bot is in the right channel
        elif ctx.voice_client.channel == ctx.author.voice.channel:
            pass  
        
        else:
            #ToDo weg mit dem print?
            await ctx.send("Tja scheisse, ne!")
            print(ctx.voice_client, ctx.author.voice)
            return
        
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            
        #if no arguments were given, play Random soundfile
        if (len(args) == 0):
            randomfile = commands_play.chooseRandomFile()
            await ctx.send('Spiele "'+randomfile+'"')
            ctx.voice_client.play(discord.FFmpegPCMAudio(os.path.join(config.soundFolder(),randomfile)))
        #Else search soundfiles for most fitting one
        else:
            #Choose file to play
            searchresult = commands_play.searchFile(*args)
            
            #If no result
            if searchresult is None:
                await ctx.send('Kein passendes Ergebnis gefunden. Mit "$tree" kannst du alle Sounds anzeigen lassen.')
            
                #Show Result and how sure BOT is that its a match
            else:
                await ctx.send('Spiele "'+str(searchresult[0])+'"\nWahrscheinlichkeit: '+str(searchresult[1]*100)[:5]+'%')
                ctx.voice_client.play(discord.FFmpegPCMAudio(os.path.join(config.soundFolder(),searchresult[0])))
        
    
    
    @bot.command(pass_context=True, name="stop", description="Stop playback")
    async def cmdStop(ctx):
        if ctx.voice_client.channel == ctx.author.voice.channel:
            ctx.voice_client.stop()
            await ctx.send("Playback stopped.")
   
   
    
    @bot.command(pass_context=True, name="youtubehaiku", aliases=["yth"], description="Return playlist of /r/youtubehaiku | youtubehaiku -time [hour, day, week, month, year, all] -amount [1-50]")
    async def cmdYTHaiku(ctx, *args):
        
        #await ctx.send(commands_reddit.youtubehaiku(args))
        commands_youtube.createPlaylist(ctx)
    
    
    
    #Establishing connection to Discord service
    try:
        bot.run(config.readini( "DISCORD", "token"))
    except Exception as e:
        logging.error("Bot failed to connect to Discord service: "+str(e))
        exit() 
        
main()