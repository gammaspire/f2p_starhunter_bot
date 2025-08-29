#config.py
#this will be where you decide where you want the bot to go!

import os
from discord import Object
from dotenv import load_dotenv

#since we are loading the variables into main.py, we have to be sure we are searching in the correct place
#for token.env! since token.env is in the config directory, we add that to the path.
load_dotenv('config/token.env')   #change the name of your token.env file here if applicable

#load the token variable - you will NOT need to change this unless you want to switch where bot is running the code!
TOKEN = os.getenv("TOKEN")

#Are you testing your slash commands and want them to appear in a specific guild only? If so, set TESTING=True. Otherwise, set TESTING=False
#TESTING=True will also send your "Welcome" messages to the testing server/channel of your choice! Otherwise, it will default to sending this message to the server in which your bot will be regularly operating.

############
TESTING=False   # CRUCIAL!
############

if TESTING:
    
    #load the TEST_GUILD variable!
    GUILD = Object(id=int(os.getenv("TEST_GUILD_ID")))
    
    #define the welcome guild and channel ID into which the bot will post a welcome message to new users (if their DMs are set to private)
    WELCOME_GUILD = os.getenv("TEST_GUILD_ID")
    WELCOME_CHANNEL = os.getenv("TEST_CHANNEL_ID")
    
else:
    
    #for the slash commands to be global (i.e., when not testing whether the slash commands work), set the necessary variables to None.)
    GUILD = None
    WELCOME_GUILD = os.getenv("STARHUNT_GUILD_ID")
    
    #define the welcome guild and channel ID into which the bot will post a welcome message to new users (if their DMs are set to private)
    WELCOME_CHANNEL = os.getenv("WELCOME_CHANNEL_ID")