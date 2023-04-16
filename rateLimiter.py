import time
from datetime import datetime
from datetime import timedelta
import leagueScraper as ls

class rateLimiter(object):
    def __init__(self):
        #Maxmimum amount of seconds left to retry a call
        self.MAX_WAIT = 2

        # Map of values that have reached their rate limit - name = routing value, value = time remaining
        self.limitedValues = {}

    # Routing value will end up getting passed in twice upon call: once for routingValue and once for *args
    # i.e. rateLimiter(func, routingValue, summonerName, routingValue)
    def __call__(self, func, routingValue, *args, **kwargs):
        #First check to see if routing value is already reached it's limit
        #If routing value is already limited, but sufficient time has passed, remove it from the map and continue
        #Else raise rate limit exception
        for key in self.limitedValues.keys():
            if key == routingValue:
                if datetime.now() > self.limitedValues[routingValue]:
                    self.limitedValues.pop(routingValue)
                    ls.logger.info(f"{routingValue} popped from limitedValues")
                    break
                else:
                    raise RateLimitExceeded

        #Send API Request
        response = func(*args, **kwargs)
        ls.apiCalls += 1

        # If the rate limit is exceeded, and more calls are available sooner than maxWait, try again after refreshTime seconds have passed
        # Else add routingValue to limited values map, refresh time to map, and raise rate limit exception
        if response.status_code == 429:
            ls.logger.info(f"Rate limiting {routingValue}")
            refreshTime = int(response.headers["Retry-After"])

            
            if refreshTime <= self.MAX_WAIT:
                ls.logger.info(f"retrying {routingValue} in {refreshTime} seconds")
                time.sleep(refreshTime)
                response = func(*args, **kwargs)
                ls.apiCalls += 1
            else:
                self.limitedValues[routingValue] = datetime.now() + timedelta(seconds = refreshTime)
                ls.logger.debug(f"rate limited values: {self.limitedValues}")
                raise RateLimitExceeded

        return response

class RateLimitExceeded(Exception):
    """Custom exception for when rate limit is exceeded and wait time too long to be handled by the application"""