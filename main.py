from discord import Intents
import os
from discord.ext import commands
import asyncio
import sys

#get this over with.
#I only ever have to add these paths (relative to main.py) once. NOT NEEDED ELSEWHERE.
sys.path.insert(0,'utils')
sys.path.insert(0, 'discord_ui')
sys.path.insert(0,'config')

from scheduler_utils import scheduler, init_scheduler_jobs, reset_star_jsons
from button_utils import restore_hoplist_view
from onready_utils import load_cogs, sync_commands
from pull_f2p_worlds import pull_f2p_worlds

from config import TOKEN, GUILD

################################################################################
################################################################################
################################################################################

#define intents; required to read message content in on_message() (see events/sad_ears.py)
intents = Intents.default()
intents.members = True   #need to detect when new members join :-)
intents.message_content = True

################################################################################
# Create custom Bot subclass to safely sync slash commands upon restart
################################################################################

class StarBot(commands.Bot):
    async def setup_hook(self):
        """
        * commands.Bot is the pre-made Discord.py bot class, with a placeholder setup_hook() function.
        * setup_hook() does NOTHING unless explicitly overwritten.
        * We want to overwrite this setup_hook() to sync slash commands before on_ready; indeed,
            when sync_commands was part of on_ready, there occasionally would be the problem of the bot
            connecting to Discord BEFORE the slash commands synchronized.
        
        SUCCINCTLY:
            setup_hook() is where the bot finishes setting itself up before Discord is allowed 
            to talk to it.
        
        setup_hook() runs exactly once, BEFORE the bot connects to Discord (i.e., before any
        events are dispatched).
        """

        #load the cogs, which are inextricably connected to the slash commands
        await load_cogs(self)
        
        #add a reference printed statement for debugging purposes
        print("LOADED COGS:", list(self.cogs.keys()))
        
        #explicitly sync slash commands BEFORE gateway connection (which occurs with on_ready)
        await sync_commands(self, GUILD)

################################################################################
################################################################################
################################################################################

#create bot instance (inherited from discord.Client)
bot = StarBot(command_prefix="$", intents=intents, help_command=None)   #I am creating my own help_command

#THIS is a flag to detect a hard vs. soft startup
#hard reset --> user runs main.py
#soft reset --> discord connection resets without terminating the python script
#Why am I using a flag? 
    #1. because this is my code and I can do what I please
    #2. on every soft reset, backup_stars.json would wipe completely. this behavior is unacceptable.
bot.first_ready = True

################################################################################
################################################################################
################################################################################

#@bot.event is used to register an event
#occurs once the bot is connected to Discord!
@bot.event
async def on_ready():    
    
    if bot.first_ready:
        print(f'[HARD RESET!] Logged in as {bot.user}')

        #clears held_stars.json and active_stars.json to begin anew (in scheduler_jobs.py)
        reset_star_jsons()
    
        #initial pull of active F2P worlds (in pull_f2p_worlds.py)
        pull_f2p_worlds()
        
        #and, of course, edit the flag
        bot.first_ready = False
    
    else:
        print(f'[SOFT RESET!] {bot.user} is reconnected.')
    
    #resumes any scheduled jobs -- such as $start_active_loop
    #also initializes the pull_f2p_worlds() job, which runs immediately and then once per 24 hours
    #(in scheduler_jobs.py)
    init_scheduler_jobs(bot)

    #if there is an existing /hoplist message, restore it. ensures the counter, etc. remains the same!
    await restore_hoplist_view(bot)
    
################################################################################
################################################################################
################################################################################    
    
bot.run(TOKEN)