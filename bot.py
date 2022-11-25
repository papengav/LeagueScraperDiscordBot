#TODO: require quotes for summonerName parameters to prevent errors
#TODO: Add commands help system
#TODO: Fix region validation
#TODO: Push to git
#TODO: Add summoner object cache


import os
import discord
from discord.ext import commands
import leagueScraper

#Establish connection to discord client
#Set command prefix to ! (exclamation mark)
bot = commands.Bot(intents=discord.Intents.all(), command_prefix='!')

@bot.event
async def on_ready():
    print("Discord connection established")

@bot.command()
async def turnOff(ctx):
    print("Disconnecting from Discord")
    await bot.close()

#Command for getting summoner rank
#Command triggerd by user typing "!rank summonerName summonerRegion"
#Validates request, and runs getRank from leagueScraper if request is valid
@bot.command()
async def rank(ctx, name, region):
    response = leagueScraper.getRank(name, region)

    await ctx.send(response)

@bot.command()
async def winRate(ctx, name, region):
    response = leagueScraper.getWinRate(name, region)

    await ctx.send(response)

@bot.command()
async def level(ctx, name, region):
    response = leagueScraper.getLevel(name, region)

    await ctx.send(response)