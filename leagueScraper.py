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
    asiaSuperRegion = ["jp1", "kr"]
    europeSuperRegion = ["eun1", "euw1", "ru", "tr1"]
    seaSuperRegion = ["oc1"]
    invalidRegion= "Please submit a valid region", *regions

#Class to store summoner information
class Summoner:
    def __init__(self, summonerV4, leagueV4, region):
        self.region = region
        self.id = summonerV4["id"]
        self.puuid = summonerV4["puuid"]
        self.iconId = summonerV4["profileIconId"]
        self.name = summonerV4["name"]
        self.level = summonerV4["summonerLevel"]
        self.matchHistory = []

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

    def getRank(self):
        return f"`{self.tier} {self.rank}` {str(self.lp)} LP"

    def getWinrate(self):
        return f"{round(100 * (self.wins / (self.wins + self.losses)))}% WR"

class Match:
    def __init__(self, matchV5):
        self.matchId = matchV5["metadata"]["matchId"]
        queueId = matchV5["info"]["queueId"]

        if queueId == 76:
            self.gameMode = "Ultra Rapid Fire"
        elif queueId == 400:
            self.gameMode = "Draft Pick"
        elif queueId == 420:
            self.gameMode = "Ranked Solo/Duo"
        elif queueId == 430:
            self.gameMode = "Blind Pick"
        elif queueId == 440:
            self.gameMode = "Ranked Flex"
        elif queueId == 450:
            self.gameMode = "ARAM"

        self.date = matchV5["info"]["gameCreation"]
        self.duration = matchV5["info"]["gameDuration"]
        self.mapId = matchV5["info"]["mapId"]
        self.participants = []

        for player in matchV5["info"]["participants"]:
            if player["teamId"] == 100:
                team = "blue"
            else:
                team = "red"

            participant = {
                "teamId": team,
                "championId": player["championId"],
                "summonerName": player["summonerName"],
                "kills": player["kills"],
                "deaths": player["deaths"],
                "assists": player["assists"],
                "cs": str(int(player["totalMinionsKilled"]) + int(player["neutralMinionsKilled"])),
                "gold": player["goldEarned"],
                "position": player["teamPosition"],
                "largestKillingSpree": player["largestKillingSpree"],
                "largestMultiKill": player["largestMultiKill"],
                "crowdControlScore": player["timeCCingOthers"],
                "damageToChamps": player["totalDamageDealtToChampions"],
                "damageToTurrets": player["damageDealtToTurrets"],
                "damageToObjectives": player["damageDealtToObjectives"],
                "damageHealed": player["totalHeal"],
                "damageTaken": player["totalDamageTaken"],
                "visionScore": player["visionScore"],
                "wardsPlaced": player["wardsPlaced"],
                "wardsDestroyed": player["wardsKilled"],
                "controlWardsPlaced": player["challenges"]["controlWardsPlaced"],
                "turretsDestroyed": player["turretKills"],
                "inhibitorsDestroyed": player["inhibitorKills"],
                "win": player["win"]
            }
            self.participants.append(participant)

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

#Requests Riot API LEAGUE-V4 - a list[dict] of a summoner's queueTypes and coorelated stats
def leagueV4(summoner, region):
    summonerId = summoner["id"]
    url = "https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerId}?api_key={apiKey}".format(
    region = region,
    summonerId = summonerId,
    apiKey = apiKey)

    return requests.get(url)

#Requests Riot API MATCH-V5 - a List[string] of match ids
def matchV5ByPuuid(summonerPuuid, region):
    superRegion = getSuperRegion(region)
    url = "https://{superRegion}.api.riotgames.com/lol/match/v5/matches/by-puuid/{summonerPuuid}/ids?start=0&count=10&api_key={apiKey}".format(
        superRegion = superRegion,
        summonerPuuid = summonerPuuid,
        apiKey = apiKey)

    return requests.get(url)

#Requests Riot API MATCH-V5 - A DTO of exhaustive match info
def matchV5ByMatchId(matchId, region):
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
            
            try:
                leagueV4RequestQueue = leagueV4Request[leagueV4Index]
            except IndexError:
                leagueV4RequestQueue = leagueV4Request
            finally: 
                response = Summoner(summonerV4 = summonerV4Request, leagueV4 = leagueV4RequestQueue, region = region)
        else:
            response = summonerV4Request.json()["status"]["message"]
    else: 
        response = invalidRegion

    return response

def getMatchHistory(summoner):
    matchIds = matchV5ByPuuid(summoner.puuid, summoner.region).json()
    matches = []
    
    for id in matchIds:
        matchV5 = matchV5ByMatchId(id, summoner.region).json()
        match = Match(matchV5)
        matches.append(match)
        
    summoner.matchHistory = matches

    return matches
