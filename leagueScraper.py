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
        if leagueV4["queueType"] == "RANKED_FLEX_SR":
            self.queueType = "Ranked Flex"
        else:
            self.queueType = "Ranked Solo/Duo"
        self.tier = leagueV4["tier"]
        self.rank = leagueV4["rank"]
        self.lp = leagueV4["leaguePoints"]
        self.wins = leagueV4["wins"]
        self.losses = leagueV4["losses"]

    def getRank(self):
        return f"`{self.tier} {self.rank}` {str(self.lp)} LP"

    def getWinrate(self):
        return f"{round(100 * (self.wins / (self.wins + self.losses)))}% WR"

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

#Returns the index of ranked solo queue in LeagueV4, if there is no solo queue history, returns ranked queue, otherwise returns whatever queue is at index 0
def getLeagueV4Index(leagueV4):
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

    return leagueV4Index

#Requests Riot API SUMMONER-V4 by Summoner Name - a DTO of summoner account info
def summonerV4ByName(summonerName, region):
    url = "https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={apiKey}".format(
    region = region,
    summonerName = summonerName,
    apiKey = apiKey)

    return requests.get(url)

#Requests Riot API SUMMONER-V4 by PUUID - a DTO of summoner account info
def summonerV4ByPuuid(summonerPuuid, region):
    url = "https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{summonerPuuid}?api_key={apiKey}".format(
        region = region,
        summonerPuuid = summonerPuuid,
        apiKey = apiKey)

    return requests.get(url)

#Requests Riot API LEAGUE-V4 - a list[dict] of a summoner's queueTypes and coorelated stats
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

#Validates and URL encodes input, invokes API request methods, returns summoner object or appropriate error message
def getSummoner(name, region):
    regionIsValid = validateRegion(region)
    name = quote(name, safe = ' ')

    if regionIsValid:
        summonerV4Request = summonerV4ByName(name, region)

        if summonerV4Request.status_code == 200:
            summonerV4Request = summonerV4Request.json()
            leagueV4Request = leagueV4(summonerV4Request, region).json()
            
            leagueV4Index = getLeagueV4Index(leagueV4Request)
            leagueV4Request = leagueV4Request[leagueV4Index]

            summoner = Summoner(summonerV4Request, leagueV4Request)

            response = summoner
        else:
            response = summonerV4Request.json()["status"]["message"]
    else: 
        response = invalidRegion

    return response
