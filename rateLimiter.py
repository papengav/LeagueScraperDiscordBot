import time
from datetime import datetime
from datetime import timedelta

class rateLimiter(object):
    def __init__(self):
        #Maxmimum amount of seconds left to retry a call
        self.MAX_WAIT = 2

        # Map of values that have reached their rate limit - name = routing value, value = time remaining
        self.limitedValues = {}

    def __call__(self, func, argOne, routingValue):
        #First check to see if routing value is already reached it's limit
        #If routing value is already limited, but sufficient time has passed, remove it from the map and continue
        #Else raise rate limit exception
        for key in self.limitedValues.keys():
            if key == routingValue:
                if datetime.now() > self.limitedValues[routingValue]:
                    self.limitedValues.pop(routingValue)
                    break
                else:
                    raise RateLimitExceeded

        #Send API Request
        response = func(argOne, routingValue)

        # If the rate limit is exceeded, and more calls are available sooner than maxWait, try again after refreshTime seconds have passed
        # Else add routingValue to limited values map, refresh time to map, and raise rate limit exception
        if response.status_code == 429:
            refreshTime = int(response.headers["Retry-After"])
            
            if refreshTime <= self.MAX_WAIT:
                time.sleep(refreshTime)
                response = func(argOne, routingValue)
            else:
                self.limitedValues[routingValue] = datetime.now() + timedelta(seconds = refreshTime)
                raise RateLimitExceeded

        return response

class RateLimitExceeded(Exception):
    """Custom exception for when rate limit is exceeded and wait time too long to be handled by the application"""