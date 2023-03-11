import requests
from urllib.parse import quote
from cachetools import cached, TTLCache
import datetime as dt
from rateLimiter import rateLimiter
import logging

#Dev Key for Riot API
#Retrieved from env and initialized in init
apiKey = None

superRegions = None
americaSuperRegion = None
asiaSuperRegion = None
europeSuperRegion = None
seaSuperRegion = None

#cache stores 100 summoners, summoners expire after 1800 seconds (30 minutes)
#follows LRU model if cache is full and no summoners are expiring 
cacheTTL = 1800
summonerCache = TTLCache(maxsize = 100, ttl = cacheTTL)

#Rate Limiter Object
limit = rateLimiter()

#Logging obejct
logger = None

def init(key):
    global apiKey
    global superRegions
    global americaSuperRegion
    global asiaSuperRegion
    global europeSuperRegion
    global seaSuperRegion
    global logger

    #Initialize Logging object
    logger = logging.getLogger('logger')

    #Create formatting for Logger
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch) 

    apiKey = key
    superRegions = ["americas", "asia", "europe", "sea"]
    americaSuperRegion = ["br1", "la1", "la2", "na1", "pbe"]
    asiaSuperRegion = ["jp1", "kr"]
    europeSuperRegion = ["eun1", "euw1", "ru", "tr1"]
    seaSuperRegion = ["oc1", "ph2", "sg2", "tw2", "th2", "vn2"]

#Class to store summoner information
class Summoner:
    def __init__(self, summonerV4, leagueV4, region):
        logger.info("Initializing summoner")
        logger.debug(f"summonerV4: {summonerV4}, leagueV4: {leagueV4}, region: {region}")
        self.region = region
        self.id = summonerV4["id"]
        self.puuid = summonerV4["puuid"]
        self.iconId = summonerV4["profileIconId"]
        self.name = summonerV4["name"]
        self.level = summonerV4["summonerLevel"]
        self.matchHistory = []
        self.refreshed = dt.datetime.now()

        if len(leagueV4) > 0:
            self.tier = leagueV4["tier"]
            self.rank = leagueV4["rank"]
            self.lp = leagueV4["leaguePoints"]
            self.wins = leagueV4["wins"]
            self.losses = leagueV4["losses"]

            if leagueV4["queueType"] == "RANKED_FLEX_SR":
                self.queueType = "Ranked Flex"
            else:
                self.queueType = "Ranked Solo/Duo"
        else:
            self.queueType = None
            self.tier = None
            self.rank = None
            self.lp = None
            self.wins = None
            self.losses = None
        
        logger.debug(f"BASE SUMMONER INFO: region: {self.region}, id: {self.id}, puuid: {self.puuid}, iconId: {self.iconId}, name: {self.name}, level: {self.level}, refreshed = {self.refreshed}")
        logger.debug(f"SUMMONER QUEUE INFO: queueType: {self.queueType}, tier: {self.tier}, rank: {self.rank}, lp: {self.lp}, wins: {self.wins}, losses: {self.losses}")
        logger.info("Summoner succesfully initialized")

    def getRank(self):
        return f"`{self.tier} {self.rank}` {str(self.lp)} LP"

    def getWinrate(self):
        return f"{round(100 * (self.wins / (self.wins + self.losses)))}% WR"

class Match:
    def __init__(self, matchV5):
        logger.info("Generating Match")
        logger.debug(f"MatchV5: {matchV5}")
        self.matchId = matchV5["metadata"]["matchId"]
        queueId = matchV5["info"]["queueId"]
        queues = {
            "0": "Custom",
            "72": "1v1 Snowdown Showdown",
            "73": "2v2 Snowdown Showdown",
            "75": "Hexakill",
            "76": "Ultra Rapid Fire",
            "78": "One For All: Mirror Mode",
            "83": "Bot Ultra Rapid Fire",
            "98": "Hexakill",
            "100": "ARAM",
            "310": "Nemesis",
            "313": "Black Market Brawlers",
            "317": "Definitely Not Dominion",
            "325": "All Random",
            "400": "Draft Pick",
            "420": "Solo/Duo Ranked",
            "430": "Blind Pick",
            "440": "Ranked Flex",
            "450": "ARAM",
            "600": "Blood Hunt Assassin",
            "610": "Dark Star: Singularity",
            "700": "Clash",
            "720": "ARAM Clash",
            "820": "Bot Match",
            "830": "Bot Match",
            "840": "Bot Match",
            "850": "Bot Match",
            "900": "ARURF",
            "910": "Ascension",
            "920": "Legend of the Poro King",
            "940": "Nexus Siege",
            "950": "Doom Bots Voting",
            "960": "Doom Bots Standard",
            "980": "Star Guardian Invasion: Normal",
            "990": "Star Guardian Invasion: Onslaught",
            "1000": "PROJECT: Hunters",
            "1010": "Snow ARURF",
            "1020": "One for All",
            "1030": "Odyssey Extraction: Intro",
            "1040": "Odyssey Extraction: Cadet",
            "1050": "Odyssey Extraction: Cremember",
            "1060": "Odyssey Extraction: Captain",
            "1070": "Odyssey Extraction: Onslaught",
            "1200": "Nexus Blitz",
            "1300": "Nexus Blitz",
            "1400": "Ultimate Spellbook",
            "1900": "Pick URF",
            "2000": "Tutorial Match",
            "2010": "Tutorial Match",
            "2020": "Tutorial Match"
        }

        self.gameMode = queues[str(queueId)]
        self.date = matchV5["info"]["gameStartTimestamp"]
        self.duration = matchV5["info"]["gameDuration"]
        self.mapId = matchV5["info"]["mapId"]
        self.participants = []

        logger.debug(f"BASE MATCH INFO: gameMode: {self.gameMode}, date: {self.date}, duration: {self.duration}, mapId: {self.mapId}")

        for player in matchV5["info"]["participants"]:
            logger.info("Generating participant")
            if player["teamId"] == 100:
                team = "blue"
            else:
                team = "red"

            participant = {
                "team": team,
                "championId": player["championId"],
                "summonerName": player["summonerName"],
                "kills": player["kills"],
                "deaths": player["deaths"],
                "assists": player["assists"],
                "cs": str(int(player["totalMinionsKilled"]) + int(player["neutralMinionsKilled"])),
                "gold": player["goldEarned"],
                "largestMultiKill": player["largestMultiKill"],
                "crowdControlScore": player["timeCCingOthers"],
                "damageToChamps": player["totalDamageDealtToChampions"],
                "damageToTurrets": player["damageDealtToTurrets"],
                "damageToObjectives": player["damageDealtToObjectives"],
                "damageHealed": player["totalHeal"],
                "damageTaken": player["totalDamageTaken"],
                "visionScore": player["visionScore"],
                "win": player["win"]
            }
            self.participants.append(participant)
            logger.debug(f"Participant: {participant}")
            logger.info("Participant succesfully generated")
        logger.info("Match succesfully generated")

#Determine which Super Region an inputed region exists within
def getSuperRegion(region):
    logger.info(f"Getting super region of {region}")
    superRegion = None

    if region in americaSuperRegion:
        superRegion = "americas"
    elif region in asiaSuperRegion:
        superRegion = "asia"
    elif region in europeSuperRegion:
        superRegion = "europe"
    elif region in seaSuperRegion:
        superRegion = "sea"

    logger.info(f"Super region {superRegion} succesfully obtained")
    return superRegion

#Returns the index of ranked solo queue in LeagueV4, if there is no solo queue history, returns ranked queue, otherwise returns whatever queue is at index 0
def getLeagueV4Index(leagueV4):
    logger.info("getLeagueV4Index called")
    logger.debug(f"leagueV4: {leagueV4}")
    
    index = 0
    leagueV4Index = None

    for queueType in leagueV4:
        if queueType["queueType"] == "RANKED_SOLO_5x5":
            leagueV4Index = index
        index += 1

    if leagueV4Index == None:
        index = 0
        for queueType in leagueV4:
            if queueType["queueType"] == "RANKED_FLEX_SR":
                leagueV4Index = index
            index += 1
    
    if leagueV4Index == None:
        leagueV4Index = 0

    logger.info(f"index {leagueV4Index} obtained")
    return leagueV4Index

#Requests Riot API SUMMONER-V4 by Summoner Name - a DTO of summoner account info
def summonerV4ByName(summonerName, region):
    logger.info(f"summonerV4ByName called with name: {summonerName} and region: {region}")
    url = "https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={apiKey}".format(
    region = region,
    summonerName = summonerName,
    apiKey = apiKey)

    logger.info("Sending summonerV4 request")
    return requests.get(url)

#Requests Riot API LEAGUE-V4 - a list[dict] of a summoner's queueTypes and coorelated stats
def leagueV4(summoner, region):
    logger.info(f"leagueV4 called with summoner: {summoner} and region: {region}")
    summonerId = summoner["id"]
    url = "https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerId}?api_key={apiKey}".format(
    region = region,
    summonerId = summonerId,
    apiKey = apiKey)

    logger.info("Sending leagueV4 request")
    return requests.get(url)

#Requests Riot API MATCH-V5 - a List[string] of match ids
def matchV5ByPuuid(summonerPuuid, superRegion):
    logger.info(f"matchV5ByPuuid called with puuid: {summonerPuuid} and super region: {superRegion}")
    url = "https://{superRegion}.api.riotgames.com/lol/match/v5/matches/by-puuid/{summonerPuuid}/ids?start=0&count=10&api_key={apiKey}".format(
        superRegion = superRegion,
        summonerPuuid = summonerPuuid,
        apiKey = apiKey)

    logger.info("Sending matchV5 request")
    return requests.get(url)

#Requests Riot API MATCH-V5 - A DTO of exhaustive match info
def matchV5ByMatchId(matchId, superRegion):
    logger.info(f"matchV5ByMatchId called with matchId: {matchId} and super region: {superRegion}")
    url = "https://{superRegion}.api.riotgames.com/lol/match/v5/matches/{matchId}?api_key={apiKey}".format(
        superRegion = superRegion,
        matchId = matchId,
        apiKey = apiKey)

    logger.info("Sending matchV5 request")
    return requests.get(url)

#Validates and URL encodes input, invokes API request methods, returns summoner object or appropriate error message
#Caches result of function to summonerCache, if parameters used parameters, retrieve cooresponding object from cache
@cached(summonerCache)
def getSummoner(name, region):
    logger.info(f"getSummoner called with name: {name} and region {region}")

    name = quote(name, safe = ' ')
    
    summonerV4Request = limit(summonerV4ByName, region, name, region)
    logger.info(f"summonerV4 status code: {summonerV4Request.status_code}")

    if summonerV4Request.status_code == 200:
        summonerV4Request = summonerV4Request.json()
        leagueV4Request = limit(leagueV4, region, summonerV4Request, region)
        logger.info(f"leagueV4 status code: {leagueV4Request.status_code}")
        leagueV4Request = leagueV4Request.json()
        
        #Determine the index at which leagueV4Request has the most applicable ranked gamemode
        leagueV4Index = getLeagueV4Index(leagueV4Request)
        
        #Length of leagueV4Request is 0 if the summoner has no ranked match history
        #Store and use the gamemode data at index previously determined, else pass on the empty, later interpreted in bot.py
        if (len(leagueV4Request) > 0):
            leagueV4RequestQueue = leagueV4Request[leagueV4Index]
        else:
            leagueV4RequestQueue = leagueV4Request

        response = Summoner(summonerV4 = summonerV4Request, leagueV4 = leagueV4RequestQueue, region = region)
    else:
        response = summonerV4Request.json()["status"]["message"]

        if summonerV4Request.status_code != 404:
            logger.warn(f"Unexpected request status code: {summonerV4Request.status_code}")

    logger.info("getSummoner succesfully ran")
    return response

#Only request new matches if the summoner doesn't already have stored matches.
#If new matches are requested, add them to the cached summoner object
def getMatchHistory(summoner: Summoner):
    logger.info(f"getMatchHistory called with summoner: {summoner}")

    if len(summoner.matchHistory) == 0:
        superRegion = getSuperRegion(summoner.region)
        matchIds = limit(matchV5ByPuuid, superRegion, summoner.puuid, superRegion)
        logger.info(f"matchIds status code: {matchIds.status_code}")
        matchIds = matchIds.json()
        matches = []
        
        for id in matchIds:
            matchV5 = limit(matchV5ByMatchId, superRegion, id, superRegion)
            logger.info(f"matchV5 status code: {matchV5.status_code}")
            matchV5 = matchV5.json()
            match = Match(matchV5)
            matches.append(match)
            
        logger.info("Match added")
        logger.debug(f"matchId: {id}")
        summoner.matchHistory = matches
    else:
        logger.info("Match History already found")
        matches = summoner.matchHistory

    logger.info("getMatchHistory succesfully ran")
    return matches
