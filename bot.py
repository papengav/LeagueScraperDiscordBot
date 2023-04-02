import discord
from discord import app_commands
from discord.ui import View
import leagueScraper as ls
import datetime as dt
import calendar
from enum import Enum
from rateLimiter import RateLimitExceeded
import traceback
import os
from dotenv import load_dotenv

#Define client and tree
#Tree holds all application commands
intents = discord.Intents.all()
client = discord.Client(intents = intents)
tree = app_commands.CommandTree(client)

devId = None
#devGuild required at runtime to create guild object for private commands only known method is to load dependancy with script
load_dotenv()
devGuildId = os.getenv('DEV_GUILD_ID')
devGuild = discord.Object(id = devGuildId)

def init(id, token):
    global devId
    devId = int(id)

    client.run(token)

class Region(Enum):
    North_America = "na1"
    Brazil = "br1"
    North_Latin_America = "la1"
    South_Latin_America = "la2"
    PBE = "pbe"
    Japan = "jp1"
    Korea = "kr"
    Philippines = "ph2"
    Singapore = "sg2"
    Taiwan = "tw2"
    Thailand = "th2"
    Vietnam = "vn2"
    North_Europe = "eun1"
    West_Europe = "euw1"
    Russia = "ru"
    Turkey = "tr1"
    Oceania = "oc1"

class LogLevel(Enum):
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10

#Construct and return select menu for match history and matches
class MatchHistorySelect(discord.ui.Select):
    def __init__(self, matchHistory: list[ls.Match], summoner: ls.Summoner):
        ls.logger.info("Generating MatchHistorySelect")
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

        ls.logger.info("MatchHistorySelect succesfully generated")
    
    async def callback(self, interaction: discord.Interaction):
        ls.logger.info("MatchHistorySelect called back")
        iterator = 0
        
        for option in self.options:
            if self.values[0] == option.value:
                view = View(timeout = None)

                if option.value == "Match History":
                    ls.logger.info("MatchHistorySelect matchHistory selected")
                    embed = matchHistoryEmbed(self.matchHistory, self.summoner)
                    view.add_item(MatchHistorySelect(self.matchHistory, self.summoner))

                    await interaction.response.edit_message(embed = embed, view = view)
                else:
                    ls.logger.info(f"MatchHistorySelect match {iterator - 1} selected")
                    embed = matchEmbed(self.matchHistory[iterator - 1], self.summoner)
                    view.add_item(MatchHistorySelect(self.matchHistory, self.summoner))
                    view.add_item(MatchSpecSelect(self.matchHistory, self.matchHistory[iterator - 1], self.summoner))
                    
                    await interaction.response.edit_message(embed = embed, view = view)

            iterator += 1

#Construct and return select menu for match specific stats
class MatchSpecSelect(discord.ui.Select):
    def __init__(self, matchHistory: list[ls.Match], match: ls.Match, summoner: ls.Summoner):
        ls.logger.info("Generating MatchSpecSelect")
        options = []
        self.matchHistory = matchHistory
        self.match = match
        self.summoner = summoner

        options.append(discord.SelectOption(label = "Match", value = "Overview", description = "Stats"))
        options.append(discord.SelectOption(label = "Blue", value = "blueStats", description = "Stats"))
        options.append(discord.SelectOption(label = "Red", value = "redStats", description = "Stats"))

        super().__init__(options = options, placeholder = "Select match view")
        
        ls.logger.info("MatchSpecSelect succesfully generated")

    async def callback(self, interaction: discord.Interaction):
        ls.logger.info("MatchSpecSelect called back")
        view = View(timeout = None)

        if self.values[0] == "Overview":
            ls.logger.info("MatchSpecSelect Overview Selected")
            embed = matchEmbed(self.match, self.summoner)
            view.add_item(MatchHistorySelect(self.matchHistory, self.summoner))
            view.add_item(MatchSpecSelect(self.matchHistory, self.match, self.summoner))

            await interaction.response.edit_message(embed = embed, view = view)

        elif self.values[0] == "blueStats":
            ls.logger.info("MatchSpecSelect blueStats selected")
            embed = matchStatsEmbed(self.match, self.summoner, "blue")
            view.add_item(MatchHistorySelect(self.matchHistory, self.summoner))
            view.add_item(MatchSpecSelect(self.matchHistory, self.match, self.summoner))

            await interaction.response.edit_message(embed = embed, view = view)

        elif self.values[0] == "redStats":
            ls.logger.info("MatchSpecSelect redStats selected")
            embed = matchStatsEmbed(self.match, self.summoner, "red")
            view.add_item(MatchHistorySelect(self.matchHistory, self.summoner))
            view.add_item(MatchSpecSelect(self.matchHistory, self.match, self.summoner))

            await interaction.response.edit_message(embed = embed, view = view)

#Construct and return embed for match history
def matchHistoryEmbed(matchHistory: list[ls.Match], summoner: ls.Summoner):
    ls.logger.info("Generating matchHistory embed")

    embed = discord.Embed(
            title = summoner.name,
            colour = discord.Colour.blue()
        )

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

    refreshedEpoch = calendar.timegm(summoner.refreshed.timetuple())
    embed.add_field(name = "".ljust(45, '-'), value = f"Region: {(summoner.region).upper()}\nRefreshed: <t:{refreshedEpoch}:f>", inline = False)

    ls.logger.info("matchHistory embed succesfully generated")
    return embed

#Construct and return embed for specific match overview
def matchEmbed(match: ls.Match, summoner: ls.Summoner):
    ls.logger.info("Generating match embed")

    for participant in match.participants:
        if participant["summonerName"] == summoner.name:
            if participant["win"] == True:
                color = discord.Colour.green()
                break
            else:
                color = discord.Colour.red()
                break

    #Unix timestamp given in miliseconds. // by 1000 to convert to seconds format for discord ui to handle with <:f##########:t>
    #double // floors division value
    matchDate = f"<t:{str(match.date // 1000)}:f>"
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

    ls.logger.info("Succesfully generated match embed")
    return embed

#format strings used in matchStatsEmbed
def fData(data):
    return str(data).ljust(10, "\u1cbc") 

def matchStatsEmbed(match: ls.Match, summoner: ls.Summoner, team: str):
    ls.logger.info("Generating matchStats embed")

    for participant in match.participants:
        if participant["summonerName"] == summoner.name:
            if participant["win"] == True:
                color = discord.Colour.green()
            else:
                color = discord.Colour.red()

    matchDate = f"<t:{str(match.date // 1000)}:f>"
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

    ls.logger.info("matchStats embed succesfully generated")
    return embed

#Construct and return embed for summoner profile
def profileEmbed(summoner: ls.Summoner):
    ls.logger.info("Generating profile embed")

    rankedEmoji = discord.utils.get(client.emojis, name = summoner.tier)

    embed = discord.Embed(
        title = summoner.name,
        description = "Level " + str(summoner.level),
        colour = discord.Colour.blue()
    )    

    embed.set_thumbnail(url = f"http://ddragon.leagueoflegends.com/cdn/12.23.1/img/profileicon/{summoner.iconId}.png")

    if summoner.queueType != None:
        embed.add_field(name = summoner.queueType, value = f"""{rankedEmoji} {summoner.getRank()}
        {str(summoner.wins)}W {str(summoner.losses)}L
        {summoner.getWinrate()}""", inline = False)
    else:
        embed.add_field(name = "Ranked", value = "No ranked match history found")

    #Discord doesn't format timestamps in footer, so added as field instead
    refreshedEpoch = calendar.timegm(summoner.refreshed.timetuple())
    embed.add_field(name = "".ljust(45, '-'), value = f"Region: {(summoner.region).upper()}\nRefreshed: <t:{refreshedEpoch}:f>", inline = False)

    ls.logger.info("Profile embed succesfully generated")
    return embed

#Construct and return embed with basic descriptions of the bots commands
def helpEmbed():
    ls.logger.info("Generating help embed")
    embed = discord.Embed(
        title = "Help Menu",
        colour = discord.Colour.blue()
    )

    embed.add_field(name = "/profile", value = "▸ Get a summoners profile.\n▸ Returns summoner's level, rank info, and winrate.", inline = False)
    embed.add_field(name = "/matches", value = "▸ Get a summoners 10 most recent matches.\n▸ Additional dropdowns allow inspection of individual matches, and more intricate data.", inline = False)
    embed.add_field(name = "Misc:", value = f"▸ Summoner profile and match data can only be refreshed every {int(ls.cacheTTL / 60)} minutes\n▸ DM Azzen#4343 with bug reports and suggestions", inline = False)

    ls.logger.info("Help embed succesfully generated")
    return embed

#Handle output if ratelimit exception has been raised
async def rateLimitHandler(interaction: discord.Interaction, deferredResponse: bool, region):
    ls.logger.warning("Rate limit exceeded: region.value")

    if (deferredResponse):
        await interaction.followup.send("LeagueScraper is currently processing the maximum amount of requests for " + region.value + ". Please try again in a couple minutes.", ephemeral = True)
    else:
        await interaction.response.send_message("LeagueScraper is currently processing the maximum amount of requests for " + region.value + ". Please try again in a couple minutes.", ephemeral = True)

#Handle application response and output if unexpected exception occured
async def exceptionHandler(interaction: discord.Interaction, deferredResponse: bool, statusCode):
    ls.logger.info(f"exceptionHandler called with {interaction} {deferredResponse} and status code {statusCode}")

    responded = False

    #Error was only API related if statusCode was int, otherwise parameter is irrelevant
    if isinstance(statusCode, int):
        #403 only occurs if API key is not provided, blacklisted, or path is invalid. Client should not make similar requests, and must be terminated if this occurs.
        #400 and 401 shouldn't occur during the natural process of the application
        if statusCode == 403:
            ls.logger.critical("Riot API responded to call with status code 403 - Forbidden API Key")
            client.close()
        #404 occurs if summoner was not found in Riot's database
        if statusCode == 404:
            if deferredResponse:
                await interaction.followup.send("Summoner not found, maybe check your spelling or region?")
            else:
                await interaction.response.send_message("Summoner not found, maybe check your spelling or region?")

            responded = True
        #500 and 503 are both server side errors. To conserve resourses, users should not be able to send further commands until issue is remedied
        elif statusCode == 500 or statusCode == 503:
            ls.logger.warn("Riot API responded to call with code " + statusCode)
            #serverErrorHandler in ls file because bot.py should not interact with Riot API.
            ls.serverErrorHandler()
        #If non-critical error followup to user if response was deferred, otherwise send normal response to user
        else:
            ls.logger.warn("Exception occured: " + traceback.format_exec())

    if not responded:
        if deferredResponse:
            await interaction.followup.send("An unexpected error was encountered while processing this request")
        else:
            await interaction.response.send_message("An unexpected error was encountered while processing this request", ephemeral = True)

#Terminal output when bot is ready for use
@client.event
async def on_ready():
    #sync global commands
    await tree.sync()
    #sync private commands
    await tree.sync(guild = devGuild)
    print("Connected to Discord")

#Turn off bot via discord command
@tree.command(name = "turnoff", description = "turn off the bot", guild = devGuild)
async def turnoff(interaction: discord.Interaction):
    if interaction.user.id == devId:
        print("Disconected from Discord")
        await interaction.response.send_message("Disconnected from Discord")
        await client.close()
    else:
        await interaction.response.send_message("Unauthorized command", ephemeral = True)

@tree.command(name = "loglevel", description = "Set terminal logging level", guild = devGuild)
async def loglevel(interaction: discord.Interaction, level: LogLevel):
    ls.logger.setLevel(level.value)
    await interaction.response.send_message(f"Logging level adjusted to {level.value}")

@tree.command(name = "help", description = "Get a description of LeagueScraper's functionality")
async def help(interaction: discord.Interaction):
    ls.logger.info("Help command called")
    ls.logger.debug(f"Discord Interaction: {interaction}")
    embed = helpEmbed()
    await interaction.response.send_message(embed = embed)

#Command to get a summoner's profile via LeagueScraper. Constructs and sends embed with returned data.
@tree.command(name = "profile", description = "Get a summoner's profile")
async def profile(interaction: discord.Interaction, name: str, region: Region):
    ls.logger.info(f"Profile command called with params: name {name} and region {region}")
    ls.logger.debug(f"Discord Interaction: {interaction}")
    try:
        deferredResponse = False
        name = name.upper()
        response = ls.getSummoner(name, region.value)

        #If request to Riot API encountered error, response will be an error message, not a summoner object
        if isinstance(response, ls.Summoner):
            await interaction.response.defer(thinking = True)
            deferredResponse = True

            summoner = response
            embed = profileEmbed(summoner)

            await interaction.followup.send(embed = embed)
        #If response type was not a Summoner, an error calling the Riot API occurred, and response is the status code. 404 is summoner not found which is an expected response.
        else:
            raise Exception
    except RateLimitExceeded:
        rateLimitHandler(interaction, deferredResponse, region.value)
    except Exception:
        await exceptionHandler(interaction, deferredResponse, response)

#Command to get a summoner's match history via LeagueScraper. Constructs and sends embed and select menu to view individual match data.
@tree.command(name = "matches", description = "Get a summoner's match history")
async def matches(interaction: discord.Interaction, name: str, region: Region):
    ls.logger.info(f"matches command called with params: name {name} and region {region}")
    ls.logger.debug(f"Discord Interaction: {interaction}")
    try:
        deferredResponse = False
        #summoner name case sensitive when testing for cache in leagueScraper.py
        name = name.upper()
        response = ls.getSummoner(name, region.value)

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
            raise Exception
    #Output proper message if rate limit for region has been reached
    except RateLimitExceeded:
        rateLimitHandler(interaction, deferredResponse, region.value)
    #If any unhandled exceptions were encountered during the code's process, call exception handler
    except Exception:
        await exceptionHandler(interaction, deferredResponse, response)