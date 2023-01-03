import leagueScraper as ls
import bot
import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    apiKey = os.getenv('RIOT_API_KEY')
    botToken = os.getenv('BOT_TOKEN')

    ls.init(apiKey)
    bot.client.run(botToken)

if __name__ == "__main__":
    main()