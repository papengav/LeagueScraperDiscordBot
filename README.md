# LeagueScraperDiscordBot
A Discord bot for retrieving League of Legends stats
(Still in early development)

leagueScraper.py - Sends and interprets request utilizing Riot Game's API
bot.py - Handles Discord integration, creating a command interface for users to interact with leagueScraper.py
botLauncher.py - Initializes the entire package along with tokens/keys from an .env file. Then connects the bot to discord for use.
RequestExceptions.py - Custom status_code exceptions for errors when sending requests with Riot's API
