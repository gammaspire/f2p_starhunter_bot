import discord
import time

from universal_utils import load_json_file, save_json_file
from SM_utils import get_SM_f2p_stars, calibrate_backups, add_SM_to_active
from star_utils import *
    
##########################################################################################
##########################################################################################
##########################################################################################

    
#creating the embed message text for ACTIVE and BACKUP star lists!      
def embed_stars(filename, embed, active=False, hold=False):
    
    """
    Populates a Discord embed with star information.

    Args:
        filename (str): Name of JSON file containing star data (active_stars.json or held_stars.json)
        embed (discord.Embed): Empty embed object to populate
        active (bool): If True, populate embed with active stars, including SM integration
        hold (bool): If True, populate embed with backup/held stars

    Returns:
        discord.Embed: Embed object populated with star information
    """
    
    #load current list of $backups (hold) or $active (active) stars
    stars = load_json_file(f'keyword_lists/{filename}')

    #pull SM stars from server
    SM_stars = get_SM_f2p_stars()

    #pull list of SM worlds (will need later)
    SM_worlds = [int(sm_star['world']) for sm_star in SM_stars]

    #if active, clean and update $active list...remove tier=0 stars, add SM stars
    if active:
        updated_stars = remove_0tier_stars(stars, SM_worlds)
        updated_stars = add_SM_to_active(updated_stars, SM_stars)

        #save updated active stars list
        save_json_file(updated_stars, f'keyword_lists/{filename}')
   
    #if hold, use original stars list read from $backups
    else:
        updated_stars = stars

    #the following will calibrate the list of backup stars with either the updated $active list or the current SM list
    
    #load list of backup/held stars
    backup_stars = load_json_file('keyword_lists/held_stars.json')
    
    #define list of active stars (just SM stars for hold=True and full $active list for active=True)
    reference_stars = SM_stars + updated_stars if active else SM_stars
    
    #update list of backup stars; prune stars with worlds in either $active or just SM
    updated_backups = calibrate_backups(reference_stars, backup_stars)
    
    #save. :-)
    save_json_file(updated_backups, 'keyword_lists/held_stars.json')

    #load location dictionary
    loc_dict = load_loc_dict()

    #for every star in updated stars list, pull the loc and find (if available) its "long name" entry
    for i,star in enumerate(updated_stars):

        star_loc = star['loc']
        
        try:
            star_full_loc = loc_dict[star_loc]
        except:
            star_full_loc = star_loc if len(star_loc)<6 else ''

        #if this is the embed for active stars, then include world, loc, current tier when sent, time remaining, and scouter who called the star
        if active:

            #get time at which star was called
            call_time = int(star['call_time'])
            
            #get current tier for the star. the routine below will change if we ever create our own runelite plugin!
            #if star is in list of SM star worlds, determine tier from SM 
            #if star is not in list of SM star worlds, use approximate_current_tier() -- gives approximate tier
                #based on when user called star in Discord server and the 7-minute-per-tier timer
            #REMINDER: star['tier'] was calibrated in add_SM_to_active() above if star in SM list!!            
            
            current_tier = approximate_current_tier(call_time, star['tier']) if int(star['world']) not in SM_worlds else star['tier']
            
            #get time remaining (in seconds) for the star! use the "current tier" above!
            time_remaining = get_time_remaining(call_time, current_tier)
            
            embed.add_field(
                    name=f'⭐ Star {i+1} ⭐',
                    value=f"{star['world']} {star_full_loc} [{star_loc}] Tier {current_tier}*\nDust time: <t:{time_remaining}:R>\nCalled by: {star['username']}",
                    inline=False
                )
        if hold:
            embed.add_field(
                name=f'⭐ Star {i+1} ⭐',
                value=f"{star['world']} {star_full_loc} [{star_loc}] Tier {star['tier']} -- {star['username']}",
                inline=False
            )

    #add 'Updated/posted [xx minutes ago]'
    timestamp=int(time.time())
    embed.add_field(name="\u200b", value=f"Posted/last updated <t:{timestamp}:R>", inline=False)
            
    return embed


##########################################################################################
##########################################################################################
##########################################################################################


#ASYNC STUFF FOR GENERATING STAR EMBEDS AND HOPLIST MESSAGES
    
#will use for sending backup and active star embeds   
#message_id only relevant for $start_active_loop. it will tell the function which embed message to modify like a bulletin board!
async def send_embed(filename, destination, active=False, hold=False, message_id=None):
    
    """
    Sends a Discord embed message containing active or backup star information.

    Args:
        filename (str): Name of JSON file containing star data (active_stars.json or held_stars.json)
        destination (discord.TextChannel | discord.Interaction): Channel or Interaction to send the embed to
        active (bool): If True, sends active stars embed
        hold (bool): If True, sends backup/held stars embed
        message_id (int, optional): If provided, updates existing message instead of sending a new one

    Returns:
        discord.Message | int: The Discord message object if sending a new message, 
                               or the message ID if updating an existing message
    """
    
    if active:
        title='Active Stars'
    else:
        title='Backup Stars'
    
    #define empty embed
    embed = discord.Embed(title=title, color=0x1ABC9C)
    
    #populate the embed message with backup or active stars, if any
    #INCLUDE FILENAME ONLY, *NOT* THE PATH TO THE FILENAME
    embed_filled = embed_stars(filename, embed, active=active, hold=hold)
    
    #if there is a message_id, then refresh the "bulletin board" attached to $start_active_loop
    if message_id:
        try:
            message = await destination.fetch_message(message_id)
            await message.edit(embed=embed_filled)
            return message.id
        
        except discord.NotFound:
            #if the message doesn't exist anymore, fallback to sending a new one
            if isinstance(destination, discord.Interaction):
                message = await destination.followup.send(embed=embed_filled)
            else:
                message = await destination.send(embed=embed_filled)
            return message.id
    else:
        if isinstance(destination, discord.Interaction):
            #respond to the interaction
            if destination.response.is_done():
                message = await destination.followup.send(embed=embed_filled)
            else:
                await destination.response.send_message(embed=embed_filled)
                message = await destination.original_response()
        else:
            message = await destination.send(embed=embed_filled)
        
        #don't use return message.id here -- need message_id to be None for $active and $backups commands
        return message