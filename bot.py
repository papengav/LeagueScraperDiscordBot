import os
import discord
from discord import app_commands
import leagueScraper as ls

#Define client and tree
#Tree holds all application commands
intents = discord.Intents.all()
client = discord.Client(intents = intents)
tree = app_commands.CommandTree(client)

devId = 394314328594972673

#Terminal output when bot is ready for use
@client.event
async def on_ready():
    await tree.sync()
    print("Discord connection established")

#Turn off bot via discord command
@tree.command(name = "turnoff", description = "turn off the bot")
async def turnoff(interaction: discord.Interaction):
    if interaction.user.id == devId:
        print("Disconnecting from Discord")
        await client.close()
    else:
        await interaction.response.send_message("Unauthorized command")

@tree.command(name = "rank", description = "Get a summoner's rank")
async def rank(interaction: discord.Interaction, name: str, region: str):
    response = ls.command(name, region, ls.getRank)

    await interaction.response.send_message(response)

@tree.command(name = "winrate", description = "Get a summoner's winrate")
async def winrate(interaction: discord.Interaction, name: str, region: str):
    response = ls.command(name, region, ls.getWinRate)

    await interaction.response.send_message(response)

@tree.command(name = "level", description = "Get a summoner's level")
async def level(interaction: discord.Interaction, name: str, region: str):
    response = ls.command(name, region, ls.getLevel)

    await interaction.response.send_message(response)