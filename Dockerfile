#import base image
FROM python:3.11.2-slim

#set directory for the source files
WORKDIR /app

#install all non-native dependancies
#text file command to install all dependancies
RUN pip install requests \
    && pip install cachetools \
    && pip install datetime \
    && pip install discord \
    && pip install python-dotenv

#copy source files
COPY bot.py .
COPY botLauncher.py .
COPY leagueScraper.py .
COPY rateLimiter.py .

#launch application
CMD python botLauncher.py
