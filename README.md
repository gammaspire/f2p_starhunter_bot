# Welcome to the F2P Starhunter Discord Bot!
This python-based bot is intended to facilitate the tracking and calling of crashed stars for the free-to-play star-hunting community (and beyond!) in Old School RuneScape. 

See our website, <dust.wiki>, for current wave times, star data, and our scouting guide!

## To host this bot locally:
* Create environment discord and install requirements.txt packages. Then, in a terminal window (assuming conda anvironment):
```
conda create -n discord
conda activate discord
cd ~/github/f2p_starhunter_bot
python main.py
```

  * Note that you will require the appropriate Discord access token in a token.env file in the same directory as main.py in order to run successfully. You are welcome to contact me directly (assuming we are collaborating on the same project!) or generate your own.
  * Additionally, you will need an API key in order to pull from the dust.wiki Dashboard (and other Google Sheets). The name of the .json file from which my key is read is found in `pull_from_gs.py`. You will likely have to create a service account on Google Cloud in order to generate your own API key, and once you do so the .json file you need will automatically download. In lieu of an API key, a workaround might involve repeatedly saving the desired sheet as a .csv file and reading the cell data from there.

## Main Commands List

* $help
    * will print an abridged version of this README document (excluding Misc. commands).

* $loc location_shorthand
    * will output what location our shorthand points to, along with a link to https://locations.dust.wiki that includes a more exact pointer to where the star spawns! 
    * e.g., `$loc nc` will output 'nc = North Crandor'

* $guide
    * Will print a link to our Scouting Guide (courtesy of WoolyClammoth!)

* $wave
    * will output current wave time, the time until end-of-wave. the clock times are Unix Epoch values that Discord automatically converts according to the reader's timezone!
    
* $poof_time f2p_world
    * will output the poof time from dust.wiki for the inputted f2p world as well as the current wave time, for ease of comparison.

* $eow f2p_world star_tier
    * will output the suggested call time from dust.wiki of a held star given the world it spawned into and its tier. additionally, there will be a more explicit message stating whether or not the star is callable.

* $hold f2p_world loc star_tier
    * Use restricted to members with @Ranked role
    * will place into dynamic JSON file the name of user who used the call, the world, location (shorthand) and tier of the star to be held. When the wave time ~ the EOW call time for the star, the bot will @ the user and output the star that can now be called. If EOW doesn't exist, will default to calling at a wave time of 85 minutes.
        * Example usage: `$hold 308 akm 8`
        *                `$hold 575 lse t7`
    
* $remove f2p_world
    * will remove any held backup star in the JSON file which corresponds to the world (which acts as a unique identifier, since there can only be one star per world).
    
* $backups
    * Use restricted to members with @Ranked role
    * will print all current backup stars in the held_stars.json file
    
* $active
    * will print all current active stars in the active_stars.json file
    * Tiers will NOT update dynamically, though the "Dust time" will (ty Unix time)

* $call f2p_world loc_shorthand star_tier
    * Use restricted to members with @Ranked role
    * calls star and places in active_stars.json file
    * note that if the star is called on SM, the tier will update to correspond to the SM tier for the star
        * Example usage: `$call 308 akm 8`
        *                `$call 575 lse t7`
        
* $start_active_loop minutes
    * Use restricted to members with @Mods role
    * will begin scheduled messages (with a frequency of every # minutes per user input) which print the list of active stars for the current wave
        * bulletin board style -- one message updated every N minutes. activate in a channel that is preferably locked to 
    * messages will print in the same channel the command is sent to
    * example usage: `$setup_active_loop 5`
        * will print every 5 minutes
    * Tiers will NOT update dynamically, though the "Dust time" will (ty Unix time)

* $stop_active_loop
    * Use restricted to members with @Mods role
    * if sent to a channel in which $setup_active_loop is active, will terminate the scheduled messages

## Miscellaneous Commands List

* $add_inspo encouraging_message
    * will add an encouraging message to the list of options that the bot will randomly select from (when it detects an "unhappy" word in a user's message)

* $inspire
    * will pull from a random assortment of inspirational messages, taken from https://zenquotes.io/api/random
    
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