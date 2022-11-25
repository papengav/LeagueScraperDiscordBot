import requests
import json
from enum import Enum
import RequestExceptions
import os
from dotenv import load_dotenv

#Dev Key for Riot API
#Retrieved from env and initialized in main
apiKey = None

#regions stores valid regions invalidRegion stores static error message for when an invalid region is inputted, probably change this later
regions = None
invalidRegion = None

def init(key):
    global apiKey
    global regions
    global invalidRegion 

    apiKey = key
    regions = ["br1", "eun1", "euw1", "jp1", "kr", "la1", "la2", "na1", "oc1", "tr1", "ru"]
    invalidRegion= "Please submit a valid region", *regions



#Class to store summoner information
class Summoner:
    def __init__(self, id, name, level, tier, rank, lp, wins, losses):
        self.id = id
        self.name = name
        self.level = level
        self.tier = tier
        self.rank = rank
        self.lp = lp
        self.wins = wins
        self.losses = losses

#Parameters: object (json object), elementName(name of element being searched)
#Returns value of json element
def getJsonElement(object, elementName):
    return object[elementName]

def convertToJson(object):
    object = object.json()

    if type(object) is list:
        object = object[0]
    
    return object
    
#Parameters: url (complete url constructed in get methods)
#Request data from Riot servers
def sendRequest(url):
    response = requests.get(url)
    
    return response

#Parameters: name (name of summoner) region (region of summoner)
#Checks if summoner and region exists returns "valid" if both are true
#If either does not exist, returns a cooresponding error message 
def requestIsValid(name, region):
    response = "valid"
    try:
        regionFound = False

        if region in regions:
            regionFound = True

        if regionFound == False:
            raise RequestExceptions.InvalidRegion
        
        summoner = summonerV4(name, region)

        if "accountId" not in summoner:
            raise RequestExceptions.SummonerDoesNotExist

    except RequestExceptions.InvalidRegion:
        response = invalidRegion
    except RequestExceptions.SummonerDoesNotExist:
        response = "Summoner does not exist."

    return response


def validateRegion(region):
    isValid = False

    if region in regions:
        isValid = True

    return isValid

def errorHandler(code):
    response = None

    try:
        if code == 400:
            raise RequestExceptions.BadRequest
        elif code == 401:
            raise RequestExceptions.Unauthorized
        elif code == 403:
            raise RequestExceptions.Forbidden
        elif code == 404:
            raise RequestExceptions.DataNotFound
        elif code == 405:
            raise RequestExceptions.MethodNotAllowed
        elif code == 415:
            raise RequestExceptions.UnsupportedMediaType
        elif code == 429:
            raise RequestExceptions.RateLimitExceeded
        elif code == 500:
            raise RequestExceptions.InternalServerError
        elif code == 504:
            raise RequestExceptions.GatewayTimeout

    except RequestExceptions.BadRequest:
        response = "Status Code 400"
    except RequestExceptions.Unauthorized:
        response = "Status code 401"
    except RequestExceptions.Forbidden:
        response = "Status code 403"
    except RequestExceptions.DataNotFound:
        response = "Summoner not found"
    except RequestExceptions.MethodNotAllowed:
        response = "Status code 405"
    except RequestExceptions.UnsupportedMediaType:
        response = "Status code 415"
    except RequestExceptions.RateLimitExceeded:
        response = "Status code 429"
    except RequestExceptions.InternalServerError:
        response = "Status code 500"
    except RequestExceptions.BadGateway:
        response = "Status code 502"
    except RequestExceptions.ServiceUnavailable:
        response = "Status code 503"
    except RequestExceptions.GatewayTimeout:
        response = "Status Code 504"

    return response
    

#Requests Riot API SUMMONER-V4
def summonerV4(summonerName, region):
    url = "https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={apiKey}".format(
    region = region,
    summonerName = summonerName,
    apiKey = apiKey)

    return sendRequest(url)

#Requests Riot API LEAGUE-V4
def leagueV4(summoner, region):
    summonerId = getJsonElement(summoner, "id")
    url = "https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerId}?api_key={apiKey}".format(
    region = region,
    summonerId = summonerId,
    apiKey = apiKey)

    return sendRequest(url)

#Parameters: name (name of the summoner), region (region of the summoner)
#Creates Summoner object for any data request regarding a summoner
def getSummoner(summonerV4, leagueV4):
    id = getJsonElement(leagueV4, "summonerId")
    name = getJsonElement(leagueV4, "summonerName")
    level = getJsonElement(summonerV4, "summonerLevel")
    tier = getJsonElement(leagueV4, "tier")
    rank = getJsonElement(leagueV4, "rank")
    lp = getJsonElement(leagueV4, "leaguePoints")
    wins = getJsonElement(leagueV4, "wins")
    losses = getJsonElement(leagueV4, "losses")

    summoner = Summoner(id, name, level, tier, rank, lp, wins, losses)

    return summoner

def getRank(name, region):
    regionIsValid = validateRegion(region)
    summonerV4Request = None
    response = None

    if regionIsValid:
        summonerV4Request = summonerV4(name, region)

        if summonerV4Request.status_code == 200:
            summonerV4Request = convertToJson(summonerV4Request)
            leagueV4Request = convertToJson(leagueV4(summonerV4Request, region))
            summoner = getSummoner(summonerV4Request, leagueV4Request)

            response =  "{name} is {tier} {rank} with {lp} lp!".format(
            name = summoner.name,
            tier = summoner.tier,
            rank = summoner.rank,
            lp = summoner.lp)
        else:
            response = errorHandler(summonerV4Request.status_code)
    else: 
        response = invalidRegion

    return response

def getWinRate(name, region):
    regionIsValid = validateRegion(region)
    summonerV4Request = None
    response = None

    if regionIsValid:
        summonerV4Request = summonerV4(name, region)

        if summonerV4Request.status_code == 200:
            summonerV4Request = convertToJson(summonerV4Request)
            
            leagueV4Request = convertToJson(leagueV4(summonerV4Request, region))
            summoner = getSummoner(summonerV4Request, leagueV4Request)
            winRate = round(100 * (summoner.wins / (summoner.wins + summoner.losses)))

            response = "{name} has {wins} wins and {losses} losses, giving them a winrate of {wr}%".format(
            name = summoner.name,
            wins = summoner.wins,
            losses = summoner.losses,
            wr = winRate)
        else:
            response = errorHandler(summonerV4Request.status_code)
    else: 
        response = invalidRegion

    return response

def getLevel(name, region):
    regionIsValid = validateRegion(region)
    summonerV4Request = None
    response = None

    if regionIsValid:
        summonerV4Request = summonerV4(name, region)

        if summonerV4Request.status_code == 200:
            summonerV4Request = convertToJson(summonerV4Request)
            leagueV4Request = convertToJson(leagueV4(summonerV4Request, region))
            summoner = getSummoner(summonerV4Request, leagueV4Request)

            response = "{name} is level {level}.".format(
            name = summoner.name,
            level = summoner.level)
        else:
            response = errorHandler(summonerV4Request.status_code)
    else: 
        response = invalidRegion

    return response