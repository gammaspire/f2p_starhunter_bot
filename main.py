import discord
import os
from discord.ext import commands
import asyncio
import sys

from pull_f2p_worlds import pull_f2p_worlds

sys.path.append('utils')
from scheduler_utils import scheduler, init_scheduler_jobs, reset_star_jsons
from button_utils import restore_hoplist_view

sys.path.append('config')
from config import TOKEN, GUILD


################################################################################
################################################################################
################################################################################

guild = GUILD

#define intents; required to read message content in on_message() (see events/sad_ears.py)
intents = discord.Intents.default()
intents.members = True   #need to detect when new members join :-)
intents.message_content = True

#create bot instance (inherits from discord.Client)
bot = commands.Bot(command_prefix="$", intents=intents, help_command=None)   #I am creating my own help_command

################################################################################
#loading the COGS!
#each Cog is a bot command or event! this function simply loads them for use.
################################################################################
async def load_cogs():
    for folder, prefix in [("./commands", "commands"), ("./events", "events")]:
        for filename in os.listdir(folder):
            if filename.endswith(".py") and filename != "__init__.py":
                #in /commands, I have __init__.py, so python treats /commands as a package
                #every .py file is its own Class, just like numpy.array or scipy.stats
                #as such, I load the extension as commands._____, with the [:-3] removing the '.py'
                ext_name = f"{prefix}.{filename[:-3]}"
                if ext_name not in bot.extensions:
                    await bot.load_extension(ext_name)

################################################################################
################################################################################
################################################################################


#@bot.event is used to register an event
@bot.event
async def on_ready():    
    
    print(f'Logged in as {bot.user}')
    
    #small delay to ensure guilds and channels are cached
    #await asyncio.sleep(1)
    
    #clears held_stars.json and active_stars.json to begin anew (in scheduler_jobs.py)
    reset_star_jsons()
    
    #initial pull of active F2P worlds (in pull_f2p_worlds.py)
    pull_f2p_worlds()
    
    #resumes any scheduled jobs -- such as $start_hop_loop and $start_active_loop
    #also initializes the pull_f2p_worlds() job, which runs immediately and then once per 24 hours
    #(in scheduler_jobs.py)
    init_scheduler_jobs(bot)
    
    #if there is an existing /hoplist message, restore it. ensures the counter, etc. remains the same!
    await restore_hoplist_view(bot)
    
    #add the Cogs!
    await load_cogs()
    
    #### Syncing slash commands
    #this will sync the commands with Discord's API.
    #it is recommended to do this only once or when you change commands.
    #if you have a lot of commands, you might want to use `sync(guild_id=GUILD_ID)` to sync only for a specific guild.
    #replace GUILD_ID with your actual guild ID if you want to limit the sync.
    #for global commands, you can use `bot.tree.sync()` without any parameters.
    #note: Global commands can take up to an hour to propagate.  
    try:
        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

################################################################################
################################################################################
################################################################################    
    
    
bot.run(TOKEN)