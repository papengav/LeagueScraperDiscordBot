# LeagueScraperDiscordBot
A Discord bot for retrieving League of Legends stats

leagueScraper.py - Sends and interprets requests utilizing Riot Game's API

bot.py - Handles Discord integration, creating a command interface for users to interact with leagueScraper.py

botLauncher.py - Initializes the package along with tokens/keys from an .env file. Then connects the bot to discord for use.

rateLimiter.py - Defines a class and custom exception to post-emptively manage Riot API rate limiting

---
LeagueScraper features three commands for users that will automatically appear when a "/" is typed into Discord's textbox.

![image](https://user-images.githubusercontent.com/35815544/219257102-6c4ca7c4-784f-4a59-b5da-54dca4aaf553.png)

Profile and Matches commands both search for data related to Summoners (League of Legends accounts). Both commands take the name and region of the summoner as parameters. An item from the region dropdown must be selected for the region parameter.

![image](https://user-images.githubusercontent.com/35815544/219257653-9ca25c1d-6bb9-4692-968f-f0ce5042de35.png)

---
**Profile Command:** Displays an embed with basic Summoner information such as their Summoner name, level, in-game profile picture, and ranked ladder info.
The footer displays the region of the Summoner, along with a timestamp of when that Summoner's data was last retreieved from Riot.

![image](https://user-images.githubusercontent.com/35815544/219257787-5886d136-a8c9-4800-b6f9-0b6891f52262.png)

---

**Matches Command:** Displays an embed with basic data on a Summoner's 10 most recent matches.
For each match, whether the Summoner won or lost is displayed along with an icon of the champion (character) they played, the game-mode, their K/D/A (Kills, Deaths, Assists), CS (how many monsters they defeated), and gold acquired during the match.

![image](https://user-images.githubusercontent.com/35815544/219258192-f00acb75-5f75-4ca4-91c7-a2fc241fceb8.png)

The dropdown menu at the bottom of the embed allows users to select and view matches in more detail, or return to the match history embed if already on a match-specific embed.

![image](https://user-images.githubusercontent.com/35815544/219258606-5c20ae74-6a21-41eb-934b-e7fbc00df147.png)

Once a specific match is selected from the dropdown, users can view the matches gamemode, the timestamp that the match started, the duration of the match, the match's map icon, along with each team's participating Summoner's champ icon, Summoner name, KDA, CS and gold.
The first dropdown can be used to view more matches, or return to the match history embed.

![image](https://user-images.githubusercontent.com/35815544/219258771-059724c4-76d3-4b34-8058-4e01cc05448c.png)

The second dropdown can be used to view even more specific data of either team's Summoners, or return to the combined stats embed, if already on a team-specific embed.

![image](https://user-images.githubusercontent.com/35815544/219259093-5e366c8a-e9c3-4a1a-be21-76f2ee4a6ac3.png)

The team-specific embed displays detailed data on each Summoner's performance in the match.
Both dropdowns are still accessible to view the other team's data, the match overview, select a new match, or return to the match history embed.

![image](https://user-images.githubusercontent.com/35815544/219259299-7e7b6d3f-037c-46e4-b233-184cdbe7e261.png)

---

**Help Command:** Displays an embed with basic info about the bot and its commands.

![image](https://user-images.githubusercontent.com/35815544/219259781-33c83f02-165a-47fd-b8c3-20a1a351d47d.png)

---

Other information:
- If an API request error occurs, users will get a message from LeagueScraper informing them of relevant information to error.
- Summoners are stored as objects, which are automatically saved to an LRU cache. Summoners expire from the cache if it reaches capacity, or if they have been in the cache for 30 minutes. New data on a Summoner can not be requested from Riot's API until they expire from the cache.
- Turnoff command is restricted to privledged users. Only Discord accounts with authorized IDs can use this command.
