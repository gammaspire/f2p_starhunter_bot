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
async def generate_hoplist_text():
    #get_ordered_worlds is async now
    worlds = await get_ordered_worlds()
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
    
    full_text = (
        "Here is a filtered list of worlds in order of early- to late-wave spawns. "
        "The list is formatted so that you can directly Copy+Paste the text into the World Cycle Runelite plugin!\n\n"
        f"```{worlds}```\n\n"
        f"-# Posted/last updated <t:{timestamp}:R>"
    )
    
    return full_text


# will use to generate (or update) the $start_hop_list message
async def send_hoplist_message(channel, message_id=None, interaction=None):
    """Fetches and edits the hoplist loop message; sends a new one if missing."""

    #generate the text (asynchronously, of course)
    text = await generate_hoplist_text()
    
    #if using a slash command interaction, do this. 
    if interaction is not None:
        #defer the interaction if not already done, so it does not time out
        #thank you.
        if not interaction.response.is_done():
            await interaction.response.defer()

        try:
            #if a message ID exists, try to fetch and edit that message
            if message_id is not None:
                msg = await channel.fetch_message(message_id)   #grab message id...
                await msg.edit(content=text)                     #edit message content...
            else:
                #if no message ID, send a fresh message
                await interaction.followup.send(text)
        except NotFound:  #in case the original message is not found, send a fresh one
            await interaction.followup.send(text)
        return

    #fallback for "traditional" prefix command usage -- just $hoplist
    if channel is None:
        print("Channel not found, skipping hoplist update.")
        return
    
    if message_id is None:
        await channel.send(text)  #send new message if no message ID
        return
    
    try:
        msg = await channel.fetch_message(message_id)  #grab message id...
        await msg.edit(content=text)                    #edit message content...
    except NotFound:  #in case the original message is not found, send a fresh one
        await channel.send(text)
