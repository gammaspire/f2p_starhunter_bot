from discord import Embed, Interaction, NotFound
import time

from universal_utils import load_json_file, save_json_file
from SM_utils import get_SM_f2p_stars, calibrate_backups, add_SM_to_active
from star_utils import remove_0tier_stars, get_clean_backups, approximate_current_tier, get_time_remaining, load_loc_dict


##########################################################################################
##########################################################################################
##########################################################################################


#generating the embed message text for ACTIVE and BACKUP star lists!     
#this text will populate the Embed initiated in send_embed()
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

    #isolate list of SM worlds (will need later)
    SM_worlds = [int(sm_star['world']) for sm_star in SM_stars]
    
    #if active=True, clean and update $active list
    if active:
        #remove tier=0 stars
        active_stars = remove_0tier_stars(stars, SM_worlds)
        
        #add SM stars
        active_stars = add_SM_to_active(active_stars, SM_stars)

        #save updated stars list!
        save_json_file(active_stars, f'keyword_lists/{filename}')
    
    else:
        active_stars = []   #dummy variable
    
    #if we are working with backup stars, just scrub the stars that have lingered past their welcome
    #that is the only self-cleaning necessary here. 
    #I unfortunately need to save held_stars.json twice. updated_stars are the GOOD stars, whereas reference_stars
    #(below) are BAD stars.
    backup_stars = get_clean_backups()
    
    #grab the SM stars as well as the cleaned list of active stars
    reference_stars = SM_stars + active_stars if active else SM_stars
    
    #update the backup stars based on the ACTIVE list!
    cleaned_backups = calibrate_backups(reference_stars, backup_stars)
    save_json_file(cleaned_backups, 'keyword_lists/held_stars.json')

    #and now, we want to convert the shorthand to the full name
    
    #load location dictionary
    loc_dict = load_loc_dict()

    #for every star in updated stars list, pull the loc and find (if available) its "long name" entry
    stars_to_render = active_stars if active else cleaned_backups  #assign list of stars to a common variable
    
    for i, star in enumerate(stars_to_render):
        star_loc = star['loc']
        try:
            star_full_loc = loc_dict[star_loc]
        except KeyError:
            star_full_loc = star_loc if len(star_loc) < 6 else ''

        #if this is the embed for active stars, include world, loc, current tier, time remaining, scouter
        if active:
            call_time = int(star['call_time'])   #when star was added to active list
            current_tier = (approximate_current_tier(call_time, star['tier'])
                            if int(star['world']) not in SM_worlds
                            else star['tier'])
            
            time_remaining = get_time_remaining(call_time, current_tier)
            embed.add_field(name=f'⭐ Star {i+1} ⭐',
                            value=f"{star['world']} {star_full_loc} [{star_loc}] Tier {current_tier}*\n"
                                  f"Dust time: <t:{time_remaining}:R>\n"
                                  f"Called by: {star['username']}",
                            inline=False)

        if hold:            
            star_message = f"{star['world']} {star_full_loc} [{star_loc}] Tier {star['tier']} -- {star['username']}\n" +\
                           f"Time to call: <t:{star['time_to_call']}:R>"
            embed.add_field(name=f'⭐ Star {i+1} ⭐',
                            value=star_message,
                            inline=False)

    #add 'Updated/posted [xx minutes ago]'
    timestamp = int(time.time())
    embed.add_field(name="\u200b", value=f"Posted/last updated <t:{timestamp}:R>", inline=False)

    return embed


##########################################################################################
##########################################################################################
##########################################################################################


#ASYNC STUFF FOR GENERATING STAR EMBEDS AND HOPLIST MESSAGES

async def _send_embed_message(destination, embed):
    """
    Helper function to handle sending or following up an embed depending on destination type.
    Either followup.send if Interaction (/command) or send if just ctx ($command)
    You know it is a helper function because of the _ prefix. ONLY used for send_embed().
    """
    if isinstance(destination, Interaction):
        if destination.response.is_done():
            return await destination.followup.send(embed=embed)
        else:
            await destination.response.send_message(embed=embed)
            return await destination.original_response()
    else:
        return await destination.send(embed=embed)


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

    title = 'Active Stars' if active else 'Backup Stars'
    embed = Embed(title=title, color=0x1ABC9C)
    embed_filled = embed_stars(filename, embed, active=active, hold=hold)

    #update existing message if message_id provided
    if message_id:
        try:
            message = await destination.fetch_message(message_id)   #retrieve message
            await message.edit(embed=embed_filled)                  #edit the embed 
            return message.id                                       #return the message ID
        except NotFound:
            pass  #fallback to sending new message

    #send a new message
    return await _send_embed_message(destination, embed_filled)


##########################################################################################
##########################################################################################
##########################################################################################


def embed_galaxy(galaxy_info):
    """
    Builds a Discord Embed for the /galaxy command!
    """

    objname = galaxy_info["objname"]
    index = galaxy_info["index"]
    failed = galaxy_info["failed"]
    source = galaxy_info["source"]
    image_url = galaxy_info["image_url"]

    message = ""
    
    if not failed:
        constellation = galaxy_info["constellation"]
        distance = int(galaxy_info["distance"])
        nducks = galaxy_info["nducks"]
        message += (f"It lies in the constellation {constellation}, "
                    f"at a distance of around {distance:,} light years from Earth.\n\n"
                    f"That is equivalent to stacking {nducks:,} Mallard ducks. Wow! :exploding_head:\n\n")
    if failed:
        message += ("It is a pity that the image retrieval of your special object failed.\n\n"
                    "Please enjoy this fun nature scene instead.\n\n")

    embed = Embed(title=f"You Pulled Galaxy {objname} (#{index})!",
                  description=message,
                  color=0x1ABC9C)

    #use thumbnail to keep text width compatible with image
    embed.set_thumbnail(url=image_url)
    embed.set_footer(text=f"Image source: {source}")

    return embed
