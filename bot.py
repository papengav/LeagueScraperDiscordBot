import discord
from discord import app_commands
from discord.ui import View
import leagueScraper as ls
import datetime as dt
import traceback

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

#Construct and return select menu for match history and matches
class MatchHistorySelect(discord.ui.Select):
    def __init__(self, matchHistory: list[ls.Match], summoner: ls.Summoner):
        options = []
        value = 1
        self.matchHistory = matchHistory
        self.summoner = summoner

        options.append(discord.SelectOption(label = self.summoner.name, value = "Match History", description = "Match History"))

        for match in self.matchHistory:
            for participant in match.participants:
                if participant["summonerName"] == self.summoner.name:
                    if participant["win"] == True:
                        win = "WIN"
                    else:
                        win = "LOSS"
                    champEmoji = discord.utils.get(client.emojis, name = str(participant["championId"]) + "id")
                    kda = "{kills}/{deaths}/{assists}".format(
                        kills = participant["kills"],
                        deaths = participant["deaths"],
                        assists = participant["assists"]
                    )
            options.append(discord.SelectOption(label = win, value = str(value), description = match.gameMode + " " + kda, emoji = champEmoji))
            value += 1

        super().__init__(options = options, placeholder = "Select a match")
    
    async def callback(self, interaction: discord.Interaction):
        iterator = 0
        
        for option in self.options:
            if self.values[0] == option.value:
                view = View(timeout = None)

                if option.value == "Match History":
                    embed = matchHistoryEmbed(self.matchHistory, self.summoner)
                    view.add_item(MatchHistorySelect(self.matchHistory, self.summoner))

                    await interaction.response.edit_message(embed = embed, view = view)
                else:
                    embed = matchEmbed(self.matchHistory[iterator - 1], self.summoner)
                    view.add_item(MatchHistorySelect(self.matchHistory, self.summoner))
                    view.add_item(MatchSpecSelect(self.matchHistory, self.matchHistory[iterator - 1], self.summoner))
                    
                    await interaction.response.edit_message(embed = embed, view = view)

            iterator += 1

#Construct and return select menu for match specific stats
class MatchSpecSelect(discord.ui.Select):
    def __init__(self, matchHistory: list[ls.Match], match: ls.Match, summoner: ls.Summoner):
        options = []
        self.matchHistory = matchHistory
        self.match = match
        self.summoner = summoner

        options.append(discord.SelectOption(label = "Match", value = "Overview", description = "Stats"))
        options.append(discord.SelectOption(label = "Blue", value = "blueStats", description = "Stats"))
        options.append(discord.SelectOption(label = "Red", value = "redStats", description = "Stats"))

        super().__init__(options = options, placeholder = "Select match view")

    async def callback(self, interaction: discord.Interaction):
        view = View(timeout = None)

        if self.values[0] == "Overview":
            embed = matchEmbed(self.match, self.summoner)
            view.add_item(MatchHistorySelect(self.matchHistory, self.summoner))
            view.add_item(MatchSpecSelect(self.matchHistory, self.match, self.summoner))

            await interaction.response.edit_message(embed = embed, view = view)

        elif self.values[0] == "blueStats":
            embed = matchStatsEmbed(self.match, self.summoner, "blue")
            view.add_item(MatchHistorySelect(self.matchHistory, self.summoner))
            view.add_item(MatchSpecSelect(self.matchHistory, self.match, self.summoner))

            await interaction.response.edit_message(embed = embed, view = view)

        elif self.values[0] == "redStats":
            embed = matchStatsEmbed(self.match, self.summoner, "red")
            view.add_item(MatchHistorySelect(self.matchHistory, self.summoner))
            view.add_item(MatchSpecSelect(self.matchHistory, self.match, self.summoner))

            await interaction.response.edit_message(embed = embed, view = view)

#Construct and return embed for match history
def matchHistoryEmbed(matchHistory: list[ls.Match], summoner: ls.Summoner):
    embed = discord.Embed(
            title = summoner.name,
            colour = discord.Colour.blue()
        )

    embed.set_footer(text = f"Region: {(summoner.region).upper()}")
    embed.set_thumbnail(url = f"http://ddragon.leagueoflegends.com/cdn/12.23.1/img/profileicon/{summoner.iconId}.png")

    matches = ""
    kdaAndCs = ""
    gold = ""

    #Find which participant is the searched summoner and output their data
    for match in matchHistory:
        for participant in match.participants:
            if participant["summonerName"] == summoner.name:
                if participant["win"] == True:
                    matches += "`WIN`".ljust(7, "\u1cbc")
                else:
                    matches += "`LOSS`".ljust(7, "\u1cbc")
                    
                matches += str(discord.utils.get(client.emojis, name = str(participant["championId"]) + "id")) + " " + match.gameMode + "\n"
                kdaAndCs += ("`{kills}/{deaths}/{assists}`".format(
                kills = participant["kills"],
                deaths = participant["deaths"],
                assists = participant["assists"]
            )).ljust(9, "\u1cbc") + "\u1cbc __" + str(participant["cs"]) + "__\n"
                gold += "__" + '{:,}'.format(participant["gold"]) + "__\n"

    embed.add_field(name = "Match History", value = matches, inline = True)
    embed.add_field(name = "KDA".ljust(8, "\u1cbc") + "CS", value = kdaAndCs, inline = True)
    embed.add_field(name = "Gold", value = gold, inline = True)

    return embed

#Construct and return embed for specific match overview
def matchEmbed(match: ls.Match, summoner: ls.Summoner):
    for participant in match.participants:
        if participant["summonerName"] == summoner.name:
            if participant["win"] == True:
                color = discord.Colour.green()
            else:
                color = discord.Colour.red()

    #Unix timestamp given in miliseconds. / by 1000 to convert to seconds for dt function
    matchDate = str(dt.datetime.fromtimestamp(match.date / 1000))
    matchDuration = str(dt.timedelta(seconds = match.duration))

    embed = discord.Embed(
        title = match.gameMode,
        description = f"{matchDate.split()[0]}\n{matchDuration}",
        colour = color
    )

    embed.set_thumbnail(url = f"http://ddragon.leagueoflegends.com/cdn/6.8.1/img/map/map{match.mapId}.png")

    blueParticipants = ""
    blueKdaAndCs = ""
    blueGold = ""

    redParticipants = ""
    redKdaAndCs = ""
    redGold = ""

    for participant in match.participants:
        if participant["team"] == "blue":
            blueParticipants += str(discord.utils.get(client.emojis, name = str(participant["championId"]) + "id")) + " " + participant["summonerName"] + "\u1cbc\n"
            blueKdaAndCs += ("`{kills}/{deaths}/{assists}`".format(
                kills = participant["kills"],
                deaths = participant["deaths"],
                assists = participant["assists"]
            )).ljust(9, "\u1cbc") + "\u1cbc __" + str(participant["cs"]) + "__\n"
            blueGold += "__" + '{:,}'.format(participant["gold"]) + "__\n"

        if participant["team"] == "red":
            redParticipants += str(discord.utils.get(client.emojis, name = str(participant["championId"]) + "id")) + " " + participant["summonerName"] + "\n"
            redKdaAndCs += ("`{kills}/{deaths}/{assists}`".format(
                kills = participant["kills"],
                deaths = participant["deaths"],
                assists = participant["assists"]
            )).ljust(9, "\u1cbc") + "\u1cbc __" + str(participant["cs"]) + "__\n"
            redGold += "__" + '{:,}'.format(participant["gold"]) + "__\n"

    #Max embed columns is 3, participant emoji and summoner name consolidated into participants field
    embed.add_field(name = "Blue Team", value = blueParticipants, inline = True)
    embed.add_field(name = "KDA".ljust(8, "\u1cbc") + "CS", value = blueKdaAndCs, inline = True)
    embed.add_field(name = "Gold", value = blueGold, inline = True)

    embed.add_field(name = "Red Team", value = redParticipants, inline = True)
    embed.add_field(name = "KDA".ljust(8, "\u1cbc") + "CS", value = redKdaAndCs, inline = True)
    embed.add_field(name = "Gold", value = redGold, inline = True)

    embed.set_footer(text = f"Region: {(summoner.region).upper()}")

    return embed

#format strings used in matchStatsEmbed
def fData(data):
    data = f"{data:,}"
    return str(data).ljust(10, "\u1cbc") 

def matchStatsEmbed(match: ls.Match, summoner: ls.Summoner, team: str):
    for participant in match.participants:
        if participant["summonerName"] == summoner.name:
            if participant["win"] == True:
                color = discord.Colour.green()
            else:
                color = discord.Colour.red()

    #Unix timestamp given in miliseconds. / by 1000 to convert to seconds for dt function
    matchDate = str(dt.datetime.fromtimestamp(match.date / 1000))
    matchDuration = str(dt.timedelta(seconds = match.duration))

    embed = discord.Embed(
        title = match.gameMode,
        description = f"{matchDate.split()[0]}\n{matchDuration}",
        colour = color,
    )

    embed.set_thumbnail(url = f"http://ddragon.leagueoflegends.com/cdn/6.8.1/img/map/map{match.mapId}.png")

    emojis = ""
    kdas = ""
    largestMultiKills = ""
    ccScores = ""
    damageToChampions = ""
    damageToTurrets = ""
    damageToObjectives = ""
    damageHealed = ""
    damageTaken = ""
    visionScore = ""

    champsAdded = 0

    #ljust not working with emojis containing strs... sloppy temp solution hard-coding unicodes
    for participant in match.participants:
        if participant["team"] == team:
            emojis += str(discord.utils.get(client.emojis, name = str(participant["championId"]) + "id"))

            #Don't add empty unicode after last champ emoji is added
            if champsAdded != 5:
                emojis += "\u1cbc\u1cbc\u1cbc\u1cbc\u1cbc\u1cbc\u1cbc"
                champsAdded += 1

            kdas += "`{kills}/{deaths}/{assists}` ".format(
                kills = participant["kills"],
                deaths = participant["deaths"],
                assists = participant["assists"]
            ).ljust(12, "\u1cbc")

            largestMultiKills += fData(participant["largestMultiKill"])
            ccScores += fData(participant["crowdControlScore"])
            damageToChampions += fData(participant["damageToChamps"])
            damageToTurrets += fData(participant["damageToTurrets"])
            damageToObjectives += fData(participant["damageToObjectives"])
            damageHealed += fData(participant["damageHealed"])
            damageTaken += fData(participant["damageTaken"])
            visionScore += fData(participant["visionScore"])

    #Last few characters of strings removed so unicodes don't wrap and create new lines
    #Discord embed constraints only allow max 3 horizontal fields with a small shared max width, makes formatting and aligning data a little sketchy
    teamStr = f"""\u1cbc\u1cbc\u1cbc\u1cbc\u1cbc {emojis}
    __KDA:__
     \u1cbc\u1cbc\u1cbc\u1cbc\u1cbc{kdas}
     __Largest Multi Kill:__
     \u1cbc\u1cbc\u1cbc\u1cbc\u1cbc{largestMultiKills[:-4]}
     __Crowd Control Score:__
     \u1cbc\u1cbc\u1cbc\u1cbc\u1cbc{ccScores[:-4]}
     __Vision Score:__
     \u1cbc\u1cbc\u1cbc\u1cbc\u1cbc{visionScore[:-4]}
     
     __Damage to Champions:__
     \u1cbc\u1cbc\u1cbc\u1cbc\u1cbc{damageToChampions[:-4]}
     __Damage to Turrets:__
     \u1cbc\u1cbc\u1cbc\u1cbc\u1cbc{damageToTurrets[:-4]}
     __Damage to Objectives:__
     \u1cbc\u1cbc\u1cbc\u1cbc\u1cbc{damageToObjectives[:-4]}
     __Damage Healed:__
     \u1cbc\u1cbc\u1cbc\u1cbc\u1cbc{damageHealed[:-4]}
     __Damage Taken:__
     \u1cbc\u1cbc\u1cbc\u1cbc\u1cbc{damageTaken[:-4]}"""

    embed.add_field(name = team.upper() + " TEAM", value = teamStr)

    return embed

#Construct and return embed for summoner profile
def profileEmbed(summoner: ls.Summoner):
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

    return embed

#Construct and return embed with basic descriptions of the bots commands
def helpEmbed():
    embed = discord.Embed(
        title = "Help Menu",
        colour = discord.Colour.blue()
    )

    embed.add_field(name = "/profile", value = "▸ Get a summoners profile.\n▸ Returns summoner's level, rank info, and winrate.", inline = False)
    embed.add_field(name = "/matches", value = "▸ Get a summoners 10 most recent matches.\n▸ Additional dropdowns allow inspection of individual matches, and more intricate data.", inline = False)

    return embed

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
        await interaction.response.send_message("Unauthorized command", ephemeral = True)

@tree.command(name = "help", description = "Get a description of LeagueScraper's functionality")
async def help(interaction: discord.Interaction):
    embed = helpEmbed()
    await interaction.response.send_message(embed = embed)

#Command to get a summoner's profile via LeagueScraper. Constructs and sends embed with returned data.
@tree.command(name = "profile", description = "Get a summoner's profile")
async def profile(interaction: discord.Interaction, name: str, region: str):
    try:
        response = ls.getSummoner(name, region)

        #If request to Riot API encountered error, response will be an error message, not a summoner object
        if isinstance(response, ls.Summoner):
            summoner = response
            embed = profileEmbed(summoner)

            await interaction.response.send_message(embed = embed)
        #send error message not summoner object. Ephemeral messages only viewable by user who invoked command
        else:
            await interaction.response.send_message(response, ephemeral = True)
    except Exception:
        exceptionDateTime = str(dt.datetime.now())

        errorLog = open("errorLog.txt", "a")
        errorLog.write(f"{exceptionDateTime}, name:{name}, region: {region}\n {traceback.format_exc()}\n")

        await interaction.response.send_message("An unexpected error was encountered while processing this request", ephemeral = True)

#Command to get a summoner's match history via LeagueScraper. Constructs and sends embed and select menu to view individual match data.
@tree.command(name = "matches", description = "Get a summoner's match history")
async def matches(interaction: discord.Interaction, name: str, region: str):
    try:
        deferredResponse = False
        response = ls.getSummoner(name, region)

        if isinstance(response, ls.Summoner):
            await interaction.response.defer(thinking = True)
            deferredResponse = True
            view = View(timeout = None)
            summoner = response
            matchHistory = ls.getMatchHistory(summoner)

            embed = matchHistoryEmbed(matchHistory, summoner)

            view.add_item(MatchHistorySelect(matchHistory, summoner))

            await interaction.followup.send(embed = embed, view = view)
        else:
            await interaction.followup.send(response, ephemeral = True)
    #If any unhandled exceptions were encountered during the code's process, log the timestamp, input parameters, and callstack to textfile
    except Exception:
        exceptionDateTime = str(dt.datetime.now())

        errorLog = open("errorLog.txt", "a")
        errorLog.write(f"{exceptionDateTime}, name:{name}, region: {region}\n {traceback.format_exc()}\n")

        #Followup if response was deferred, otherwise send sole response to user
        if (deferredResponse):
            await interaction.followup.send("An unexpected error was encountered while processing this request", ephemeral = True)
        else:
            await interaction.response.send_message("An unexpected error was encountered while processing this request", ephemeral = True)