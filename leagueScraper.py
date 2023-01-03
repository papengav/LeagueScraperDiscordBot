import requests
from urllib.parse import quote

#Dev Key for Riot API
#Retrieved from env and initialized in init
apiKey = None

regions = None
superRegions = None
americaSuperRegion = None
asiaSuperRegion = None
europeSuperRegion = None
seaSuperRegion = None
invalidRegion = None

def init(key):
    global apiKey
    global regions
    global superRegions
    global americaSuperRegion
    global asiaSuperRegion
    global europeSuperRegion
    global seaSuperRegion
    global invalidRegion 

    apiKey = key
    regions = ["br1", "eun1", "euw1", "jp1", "kr", "la1", "la2", "na1", "oc1", "tr1", "ru"]
    superRegions = ["americas", "asia", "europe", "sea"]
    americaSuperRegion = ["br1", "la1", "la2", "na1"]
    asiaSuperRegion = ["jp1", "kr", "tr1"]
    europeSuperRegion = ["eun1", "euw1", "ru"]
    seaSuperRegion = ["oc1"]
    invalidRegion= "Please submit a valid region", *regions

#Class to store summoner information
class Summoner:
    def __init__(self, summonerV4, leagueV4):
        self.id = leagueV4["summonerId"]
        self.puuid = summonerV4["puuid"]
        self.iconId = summonerV4["profileIconId"]
        self.name = leagueV4["summonerName"]
        self.level = summonerV4["summonerLevel"]
        self.tier = leagueV4["tier"]
        self.rank = leagueV4["rank"]
        self.lp = leagueV4["leaguePoints"]
        self.wins = leagueV4["wins"]
        self.losses = leagueV4["losses"]

def validateRegion(region):
    isValid = False

    if region in regions:
        isValid = True

    return isValid
    
#Determine which Super Region an inputed region exists within
def getSuperRegion(region):
    superRegion = None

    if region in americaSuperRegion:
        superRegion = "americas"
    elif region in asiaSuperRegion:
        superRegion = "asia"
    elif region in europeSuperRegion:
        superRegion = "europe"
    elif region in seaSuperRegion:
        superRegion = "sea"

    return superRegion


#Requests Riot API SUMMONER-V4 by Summoner Name - a DTO of in game summoner info
def summonerV4ByName(summonerName, region):
    url = "https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={apiKey}".format(
    region = region,
    summonerName = summonerName,
    apiKey = apiKey)

    return requests.get(url)

#Requests Riot API SUMMONER-V4 by PUUID - a DTO of in game summoner info
def summonerV4ByPuuid(summonerPuuid, region):
    url = "https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{summonerPuuid}?api_key={apiKey}".format(
        region = region,
        summonerPuuid = summonerPuuid,
        apiKey = apiKey)

    return requests.get(url)

#Requests Riot API LEAGUE-V4 - a DTO of summoner account info
def leagueV4(summoner, region):
    summonerId = summoner["id"]
    url = "https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerId}?api_key={apiKey}".format(
    region = region,
    summonerId = summonerId,
    apiKey = apiKey)

    return requests.get(url)

#Requests Riot API MATCH-V5 - a List[string] of match ids
def MatchV5ByPuuid(summonerPuuid, region):
    superRegion = getSuperRegion(region)
    url = "https://{superRegion}.api.riotgames.com/lol/match/v5/matches/by-puuid/{summonerPuuid}/ids?api_key={apiKey}".format(
        superRegion = superRegion,
        summonerPuuid = summonerPuuid,
        apiKey = apiKey)

    return requests.get(url)

#Requests Riot API MATCH-V5 - A DTO of exhaustive match info
def MatchV5ByMatchId(matchId, region):
    superRegion = getSuperRegion(region)
    url = "https://{superRegion}.api.riotgames.com/lol/match/v5/matches/{matchId}?api_key={apiKey}".format(
        superRegion = superRegion,
        matchId = matchId,
        apiKey = apiKey)

    return requests.get(url)

def getRank(summoner):
    return "{name} is {tier} {rank} with {lp} lp!".format(
    name = summoner.name,
    tier = summoner.tier,
    rank = summoner.rank,
    lp = summoner.lp)

def getWinRate(summoner):
    winRate = round(100 * (summoner.wins / (summoner.wins + summoner.losses)))

    return "{name} has {wins} wins and {losses} losses, giving them a winrate of {wr}% ".format(
    name = summoner.name,
    wins = summoner.wins,
    losses = summoner.losses,
    wr = winRate)

def getLevel(summoner):
    return "{name} is level {level}.".format(
    name = summoner.name,
    level = summoner.level)

#Generalized function all interactions pass through. Invokes API methods to construct a summoner object, then passes off object to desired command.
def command(name, region, func):
    regionIsValid = validateRegion(region)
    summonerV4Request = None
    response = None
    name = quote(name, safe = ' ')

    if regionIsValid:
        summonerV4Request = summonerV4ByName(name, region)

        if summonerV4Request.status_code == 200:
            summonerV4Request = summonerV4Request.json()
            leagueV4Request = leagueV4(summonerV4Request, region).json()[0]
            summoner = Summoner(summonerV4Request, leagueV4Request)

            response = func(summoner)
        else:
            response = summonerV4Request.json()["status"]["message"]
    else: 
        response = invalidRegion

    return response
