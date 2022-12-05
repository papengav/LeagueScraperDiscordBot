#TODO: require quotes for summonerName parameters to prevent errors
#TODO: Add commands help system
#TODO: Fix region validation
#TODO: Add summoner object cache
#TODO: Only privledged users (devs) can call turnOff method
#TODO: Handle null bot command parameters
#TODO: Rework Exception System

import os
import discord
from discord.ext import commands
import leagueScraper as ls

#Establish connection to discord client
#Set command prefix to ! (exclamation mark)
bot = commands.Bot(intents=discord.Intents.all(), command_prefix='!')

#Termianl output when bot is ready for use
@bot.event
async def on_ready():
    print("Discord connection established")

#Turn off bot via discord command
@bot.command()
async def turnOff(ctx):
    print("Disconnecting from Discord")
    await bot.close()

@bot.command()
async def Rank(ctx, name, region):
    response = ls.command(name, region, ls.getRank)

    await ctx.send(response)

@bot.command()
async def Winrate(ctx, name, region):
    response = ls.command(name, region, ls.getWinRate)

    await ctx.send(response)

@bot.command()
async def Level(ctx, name, region):
    response = ls.command(name, region, ls.getLevel)

    await ctx.send(response)
