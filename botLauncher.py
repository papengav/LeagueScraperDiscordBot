import leagueScraper
import bot
import os
from dotenv import load_dotenv
import discord

def main():
    load_dotenv()
    apiKey = os.getenv('RIOT_API_KEY')
    botToken = os.getenv('BOT_TOKEN')

    leagueScraper.init(apiKey)
    bot.client.run(botToken)

if __name__ == "__main__":
    main()