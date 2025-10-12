# Welcome to the F2P Starhunter Discord Bot!
This python-based bot is intended to facilitate the tracking and calling of crashed stars for the free-to-play star-hunting community (and beyond!) in Old School RuneScape (OSRS). 

See our website, <dust.wiki>, for current wave times, star data, and our scouting guide! You can also find our link to the Discord server where the OG F2P Starhunter bot is happily executing commands at our will.

Also check out *F2P Starhunt*, our in-game OSRS community chat channel.

## To host this bot locally:
* If using Conda, create an environment called `discord` and install requirements.txt packages. Then, run the main script in a terminal window or whatever python editor or shell you use:
```
conda create -n discord
conda activate discord
cd ~/github/f2p_starhunter_bot
python main.py
```
* There are a few *critical* requirements in order to prepare the directory correctly for your Discord bot to run. You should start with creating a file called `token.env` and put it in the /config directory. You will then need to populate it with the following:
    * TOKEN=your_discord_access_token
        * your_discord_access_token is associated with the Discord bot or application you created for executing this code. If you have not already, you can begin that journey at <https://discord.com/developers/applications>.
    * SHEET_ID=17rGbgylW_IPQHaHUW1WsJAhuWI7y2WhplQR79g-obqg
        * this uncanny string of characters is the Google Sheets ID of <dust.wiki>. Because this is publicly available, I paste it here for convenience.
    * STARHUNT_GUILD_ID=starhunt_guild_id
        * starhunt_guild_id is the Discord server ID where the bot will be active. You can find this by right-clicking the server icon on the Desktop app and clicking "Copy Server ID" at the bottom of the popup menu.
    * WELCOME_CHANNEL_ID=welcome_channel_id
        * this one is optional, depending on whether you want to spam a new member to your server with a welcome message. The bot defaults to a DM, but if that user has DM privacy settings enabled it will instead send the message to the welcome_channel_id. You can find this ID the same way as you found the guild ID, but by instead right-clicking the desired channel in your server.

* Be sure to update the config/configs.py file to check if you are loading the correct guild/channel variables from token.env into your bot! There are a few commented instructions in the .py file about what to do and why you might want to do it.

* Additionally, you will need an API key in order to pull from the dust.wiki Dashboard (and other Google Sheets). The name of the .json file from which my key is read is found in `/utils/googlesheet_utils.py`. You will likely have to create a service account on Google Cloud in order to generate your own API key, and once you do so the .json file you need will automatically download. In lieu of an API key, a workaround might involve repeatedly saving the desired sheet as a .csv file and reading the cell data from there. The code is not set up for this, so you will have to fiddle around with some of the scripts in /utils. :-)

* And, lastly...you may notice that a few files are missing from /keyword_lists. That is okay! There files are not integral to the basic functioning of the code and largely are for the miscellaneous commands (see below). You have full creative license to create your own!

## Main Commands List
### Note that every prefix command listed below has a slash command variant! Just replace the $ with / in the Discord textbox.

* $help
    * will print an abridged version of this README document (excluding Misc. commands).

* $loc location_shorthand
    * will output what location our shorthand points to, along with a link to https://locations.dust.wiki that includes a more exact pointer to where the star spawns! 
    * e.g., `$loc nc` will output 'nc = North Crandor'

* $guide
    * Will print a link to our F2P Starhunt Scouting Guide.

* $wave
    * will output current wave time, the time until end-of-wave. the clock times are Unix Epoch values that Discord automatically converts according to the reader's timezone!

* $hoplist
    * will output a list of list of worlds, ordered from early-wave to late-wave to no-wave spawns and with $active and $backups star worlds filtered out.
    * this list is formatted such that users can directly copy+paste the output into the World Cycle Runelite plugin.
    * worlds with no data are tacked on at the end in numerical order
    * also includes a REFRESH button!
    
* $poof_time f2p_world
    * will output the poof time from dust.wiki for the inputted f2p world as well as the current wave time, for ease of comparison.
        * Example usage: `$poof_time 308`

* $eow f2p_world star_tier
    * will output the suggested call time from dust.wiki of a held star given the world it spawned into and its tier. additionally, there will be an additional message stating whether or not the star is callable.
        * Example usage: `eow 308 9`

* $hold f2p_world loc star_tier
    * Use restricted to members with @Ranked role
    * will place into dynamic JSON file the name of user who used the call, the world, location (shorthand) and tier of the star to be held. When the wave time ~ the EOW call time for the star, the bot will @ the user and output the star that can now be called. If EOW doesn't exist, will default to calling at a wave time corresponding to the tier such that if you were to begin mining that star immediately, it would last at least until the end of the spawn period (+45) of the new wave.
        * Example usage: `$hold 308 akm 8`

* /offload @rankeduser
    * **SLASH COMMAND ONLY!**
    * Use restricted to members with @Ranked role
    * will change the "person to ping" from the author (the one who called the command) to the target (the @rankeduser) stars in held_stars.json file. The author MUST have backup stars associated with their username for this to work, otherwise there will be a snarky message from the bot.
        * Example usage: `/offload @gammasquire`

* $remove f2p_world
    * will remove any held backup star in the JSON file which corresponds to the world (which acts as a unique identifier, since there can only be one star per world).
        * Example usage: `$remove 308`
    
* $backups
    * Use restricted to members with @Ranked role
    * will print all current backup stars in the held_stars.json file
        * Example usage: `$backups`
    
* $active
    * will print all current active stars in the active_stars.json file
    * Tiers will NOT update dynamically, though the "Dust time" will (ty Unix time)
        * Example usage: `$active`

* $lost_worlds
    * will print any currently inactive F2P worlds that still linger on the dust.wiki spreadsheet
        * Example usage: `$lost_worlds`

* $call f2p_world loc_shorthand star_tier
    * Use restricted to members with @Ranked role
    * calls star and places in active_stars.json file
    * note that if the star is called on SM, the tier will update to correspond to the SM tier for the star
        * Example usage: `$call 308 akm 8`
        
* $start_active_loop minutes
    * Use restricted to members with @Mods role
    * will begin scheduled messages (with a frequency of every # minutes per user input) which print the list of active stars for the current wave
        * bulletin board style -- one message updated every N minutes. activate in a channel that is preferably locked to any non-mod messages
    * messages will print in the same channel the command is sent to
    * example usage: `$start_active_loop 5`
        * will print every 5 minutes
    * Tiers will NOT update dynamically, though the "Dust time" will (ty Unix time)

* $stop_active_loop
    * Use restricted to members with @Mods role
    * if sent to a channel in which $start_active_loop is active, will terminate the scheduled messages    

## Miscellaneous Commands List

* $add_inspo encouraging_message
    * will add an "encouraging" message to the list of options that the bot will randomly select from when it detects an "unhappy" word in a user's message
    * Example Usage: $add_inspo Have you considered that maybe you should stop feeling that way?

* $inspire
    * will pull a randomly-generated quote from Dave Tamowski's "Disappointing Affirmations" 

* $rand
    * will print a random factoid for your amusement, taken from https://uselessfacts.jsph.pl/

* $joke 
    * will print a random joke, pulling from a list written by our very own tj44
    * this list is available upon request; otherwise will default to a list of two jokes
    
* $conch
    * will prompt user to type a yes/no question within a 15 second timeframe
    * if response is detected, code will pull randomly from list of possible responses
    
* $strike
    * will print words of forceful "encouragement" to press our leaders into allowing the scouters to unionize
    

## Notes

* The base of this code originated from https://www.freecodecamp.org/news/create-a-discord-bot-with-python/.
* Buyer beware: this tool may be afflicted by the spaghetti plague. I claim all responsibility for this.
