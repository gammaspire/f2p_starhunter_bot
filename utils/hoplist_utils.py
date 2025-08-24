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
def generate_hoplist_text():
    worlds = get_ordered_worlds()  
    stars = load_json_file(f'keyword_lists/active_stars.json')
    
    #isolate active worlds
    #in worlds string, worlds.replace($active world,"") -- that is, filter out the active worlds
    for star in stars:
        world = str(star['world'])
        #remove $active worlds along with their comma. if world is the last world in string, there is a leading comma.
        worlds = worlds.replace(world+',','') if world != worlds[-3:] else worlds.replace(','+world,'')
    
    #remove any starting/ending commas that may have regrettably been left behind. just in case.
    worlds = worlds.strip(',')
    
    #grab the time...
    timestamp = int(time.time())
    
    full_text = "Here is a filtered list of worlds in order of early- to late-wave spawns. The list is formatted so that you can directly Copy+Paste the text into the World Cycle Runelite plugin!\n\n```" + worlds + "```\n\n" + f"-# Posted/last updated <t:{timestamp}:R>"
    
              
    return full_text


#will use to generate (or update) the $start_hop_list message
async def send_hoplist_message(channel, message_id):
    """Fetches and edits the hoplist loop message; sends a new one if missing."""
    text = generate_hoplist_text()
    if channel is None:
        print("Channel not found, skipping hoplist update.")
        return
    if message_id is None:
        await channel.send(text)
        return
    
    try:
        msg = await channel.fetch_message(message_id)   #grab message id...
        await msg.edit(content=text)                    #edit message content...
    except NotFound:                            #in case the original message is not found, send a fresh one
        await channel.send(text)