############################################################
#functions to create the filtered list of f2p worlds
#used for commands/hoplist.py and commands/start_hop_loop.py
############################################################

import sys
import time
from discord import NotFound

from universal_utils import load_json_file
from googlesheet_utils import get_ordered_worlds

#generate the actual "hoplist" text for when I send the $hoplist message
async def generate_hoplist_worlds():
    #get_ordered_worlds is async now
    worlds = await get_ordered_worlds()
    active_stars = load_json_file(f'keyword_lists/active_stars.json')
    
    #also load backup stars!
    held_stars = load_json_file(f'keyword_lists/held_stars.json')
    
    stars = active_stars+held_stars
    
    #isolate active worlds
    #in worlds string, worlds.replace($active world,"") -- that is, filter out the active worlds
    for star in stars:
        world = str(star['world'])
        #remove active worlds along with their comma. if world is the last world in string, there is a leading comma.
        worlds = worlds.replace(world+',','') if world != worlds[-3:] else worlds.replace(','+world,'')
        
    #remove any starting/ending commas that may have regrettably been left behind. just in case.
    worlds = worlds.strip(',')
     
    return worlds


async def generate_hoplist_message(channel, msg=None, refresh_count=0):
    
    #generate the text (asynchronously, of course)
    worlds = await generate_hoplist_worlds()
    
    #if msg variable is not None (meaning we are editing a previously existing message), then pull its time of creation
    #otherwise, 'set' its time of creation as NOW
    if msg is not None:
        sent_time = int(msg.created_at.timestamp())    #.timestamp() converts to UNIX format!
    else:
        sent_time = int(time.time())
    
    timestamp = int(time.time())
    
    text = (
        "List of F2P worlds in order of early- to late-wave to 'no-data' spawns.\n"
        "- Directly Copy+Paste the text into the World Cycle Runelite plugin\n"
        "- Worlds without data are tacked on at the end in numerical order\n"
        "- Worlds in which there is a known active or held star are filtered out\n"
        f"```{worlds}```\n"
        f"-# Refreshes since <t:{sent_time}:R>: {refresh_count}\n"
        f"-# Time since last refresh: <t:{timestamp}:R>")
    
    return text
    

#will use to generate (or update) the $start_hop_list message
async def send_hoplist_message(channel, message_id=None, interaction=None, refresh_count=0):
    """Fetches and edits the hoplist loop message; sends a new one if missing.
       Always returns the message object."""
    
    if message_id is not None:
        msg = await channel.fetch_message(message_id)
    else:
        msg = None
    
    #generate the text (asynchronously, of course)
    text = await generate_hoplist_message(channel, msg, refresh_count=refresh_count)
    
    ###
    #if using a slash command interaction, do all of this. 
    ###
    if interaction is not None:
        if not interaction.response.is_done():
            await interaction.response.defer()
        
        try:
            
            if msg is not None:
                #msg already defined above if message_id is not None!
                await msg.edit(content=text)
                return msg
            else:
                msg = await interaction.followup.send(text, wait=True)  #wait=True ensures the Message object is saved
                return msg
        
        except NotFound:
            msg = await interaction.followup.send(text, wait=True)
            return msg
    
    ###
    #fallback for "traditional" prefix command usage -- just $hoplist
    ###
    if channel is None:
        print("Channel not found, skipping hoplist update.")
        return None
    
    if message_id is None:
        msg = await channel.send(text)
        return msg
    
    try:
        msg = await channel.fetch_message(message_id)
        await msg.edit(content=text)
        return msg
    
    except NotFound:
        msg = await channel.send(text)
        return msg