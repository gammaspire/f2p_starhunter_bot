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

## Main Commands List
* $loc location_shorthand
    * will output what location our shorthand points to, along with a link to https://locations.dust.wiki that includes a more exact pointer to where the star spawns! e.g., `$loc nc` will output 'nc = North Crandor'.

*

## Misc. Commands List

* $add encouraging_message
    * will add an encouraging message to the list of options that the bot will select from (when it detects a "sad" word in a user's message)

* $inspire
    * will pull from a random assortment of inspirational messages, taken from https://zenquotes.io/api/random

* $guide
    * Will print a link to out Scouting Guide (courtesy of WoolyClammoth!)