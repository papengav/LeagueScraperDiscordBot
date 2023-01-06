import leagueScraper as ls
import bot
import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    apiKey = os.getenv('RIOT_API_KEY')
    devId = os.getenv('DEV_ID')
    botToken = os.getenv('BOT_TOKEN')

    ls.init(apiKey)
    bot.init(devId, botToken)

def closeBot():
    bot.client.close()

if __name__ == "__main__":
    main()