import discord
from discord import app_commands
import leagueScraper as ls
import time

#Define client and tree
#Tree holds all application commands
intents = discord.Intents.all()
client = discord.Client(intents = intents)
tree = app_commands.CommandTree(client)

devId = None

def init(id, token):
    global devId
    devId = int(id)

    client.run(token)


#Terminal output when bot is ready for use
@client.event
async def on_ready():
    await tree.sync()
    print("Discord connection established")

#Turn off bot via discord command
@tree.command(name = "turnoff", description = "turn off the bot")
async def turnoff(interaction: discord.Interaction):
    if interaction.user.id == devId:
        await interaction.response.send_message("Disconnecting", ephemeral = True)
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

        if summoner.queueType != None:
            embed.add_field(name = summoner.queueType, value = f"""{rankedEmoji} {summoner.getRank()}
            {str(summoner.wins)}W {str(summoner.losses)}L
            {summoner.getWinrate()}""", inline = False)
        else:
            embed.add_field(name = "Ranked", value = "No ranked match history found")

        await interaction.response.send_message(embed = embed)
    else:
        await interaction.response.send_message(response, ephemeral = True)

@tree.command(name = "matches", description = "Get a summoner's match history")
async def matches(interaction: discord.Interaction, name: str, region: str):
    response = ls.getSummoner(name, region)

    if isinstance(response, ls.Summoner):
        await interaction.response.defer(thinking = True)
        summoner = response
        matchHistory = ls.getMatchHistory(summoner)

        embed = discord.Embed(
            title = summoner.name,
            colour = discord.Colour.blue()
        )

        embed.set_footer(text = f"Region: {(summoner.region).upper()}")
        embed.set_thumbnail(url = f"http://ddragon.leagueoflegends.com/cdn/12.23.1/img/profileicon/{summoner.iconId}.png")

        matchHistoryStr = ""

        for match in matchHistory:
            matchStr = ""

            for participant in match.participants:
                if participant["summonerName"] == summoner.name:
                    champEmoji = str(discord.utils.get(client.emojis, name = str(participant["championId"])))

                    if participant["win"] == True:
                        winStatus = "**WIN**"
                    else:
                        winStatus = "**LOSS**"
                        
                    gameMode = match.gameMode
                    kda = "{kills}/{deaths}/{assists}".format(
                        kills = participant["kills"],
                        deaths = participant["deaths"],
                        assists = participant["assists"]
                    )
                    cs = str(participant["cs"])
                    gold = '{:,}'.format(participant["gold"])
                    
                    matchStr = f"**{winStatus}** \u1CBC {gameMode} \u1CBC {champEmoji} `{kda}` \u1CBC\u1CBC __{cs}__CS \u1CBC __{gold}__ Gold\n"

            matchHistoryStr += matchStr

        embed.add_field(name = "Match History", value = matchHistoryStr)

        await interaction.followup.send(embed = embed)
    else:
        await interaction.response.send_message(response, ephemeral = True)