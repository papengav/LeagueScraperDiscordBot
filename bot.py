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

@tree.command(name = "profile", description = "Get a summoner's profile")
async def profile(interaction: discord.Interaction, name: str, region: str):
    response = ls.getSummoner(name, region)

    if isinstance(response, ls.Summoner):
        summoner = response
        rankedEmoji = discord.utils.get(client.emojis, name = summoner.tier)

        embed = discord.Embed(
            title = summoner.name,
            description = "Level " + str(summoner.level),
            colour = discord.Colour.blue()
        )

        embed.set_footer(text = f"Region: {(summoner.region).upper()}")
        embed.set_thumbnail(url = f"http://ddragon.leagueoflegends.com/cdn/12.23.1/img/profileicon/{summoner.iconId}.png")
        embed.add_field(name = summoner.queueType, value = f"""{rankedEmoji} {summoner.getRank()}
        {str(summoner.wins)}W {str(summoner.losses)}L
        {summoner.getWinrate()}""", inline = False)

        await interaction.response.send_message(embed = embed)
    else:
        await interaction.response.send_message(response, ephemeral = True)