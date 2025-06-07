import requests
import json
import os
import random
import time
from pull_stars_from_SM import *
from universal_functions import *



############################################################
#Print the key to our shorthand for star spawning locations!
#use: 
#   $loc shorthand
#e.g., '$loc nc' will output 'North Crandor'
############################################################

def load_loc_dict():
    loc_dict = {}
    with open("keyword_lists/locs.txt") as f:
        for line in f:
            try:
                key = line.split()[0]
                val = line.split()[1]
                val = val.replace('_',' ')
                loc_dict[key] = val
            except:
                continue
    return loc_dict

def print_loc_key(message):
    try:
        loc_dict = load_loc_dict()
    except:
        print('Oh no! keyword_lists/locs.txt not found or corrupted!')
        return
    
    loc_shorthand = message.content[5:].strip()     #removes '$loc ' from string
    try:
        return loc_shorthand, loc_dict[loc_shorthand]
    except:
        return 'Location invalid! See https://locations.dust.wiki for a list of our shorthand.'
    
############################################################
#print wave guide URL into the chat!
#use:
#    $guide
############################################################

def print_guide():
    return 'Check out out Scouting Guide [Here!](https://docs.google.com/presentation/d/17bU-vGlOuT0MHBZ9HlTrfQEHKT4wHnBrLTV2_HC8LQU/)'

############################################################
#hold star in held_stars.json file OR add star to active_stars.json
#use: 
#   $hold world loc tier
#   $call world loc tier
#e.g., 
#   $hold 308 nc 8
#   $call 308 nc 8
############################################################

#using JSON file --> a convenient approach to storing dictionary keys. :-)
def add_star_to_list(username,user_id,world,loc,tier,filename='held_stars.json'):

    #grab time at which star is CALLED --> will use to determine star tier later on
    call_time = time.time()

    #isolate the tier number in case someone entered t# or T#
    tier = remove_frontal_corTex(tier)

    stars_list = load_json_file(f'keyword_lists/{filename}')

    stars_list.append({
        "username": username,
        "user_id": user_id,
        "world": world,
        "loc": loc,
        "tier": tier,
        "call_time": call_time
    })

    with open(f'keyword_lists/{filename}','w') as f:
        json.dump(stars_list, f, indent=6)   #indent indicates number of entries per array?

def print_error_message():
    message = 'Missing or invalid arguments!\nSyntax: $hold world loc tier\nWorld should be F2P, loc must be one of our shorthand keys, and the tier must be 6-9 for held star or 1-9 for active star.\nExample: $hold 308 akm 8'
    return message
        
############################################################
#remove star from held_stars.json ($remove_held) OR active_stars.json ($poof)
#use: 
#   $remove_held world
#   $poof world
#e.g., 
#   $remove_held 308
#   $poof 308
############################################################
        
def remove_star(world,filename='held_stars.json',output_data=False):
    #remove star from the .json
    all_held_stars = load_json_file(f'keyword_lists/{filename}')
    
    #if output_data needed for the $remove command (meaning that the command returns the Loc and Tier associated with the star), grab that information and assign to variables
    if output_data:
        #creating variable placeholders...just in case
        loc=''
        tier=''
        for n in all_held_stars:
            if n['world']==world:
                loc=n['loc']
                tier=n['tier']
    
    #the WORLD is the only unique identifier for every entry -- remove entry corresponding to world!
    updated_held_stars = [entry for entry in all_held_stars if entry["world"] != str(world)]
    
    save_json_file(updated_held_stars, f'keyword_lists/{filename}')
    
    if output_data:
        return loc,tier  
      
    
############################################################
#print list of star backups being held in the current wave
#OR
#print list of active stars this current wave
#use: 
#   $backups
#   $active
############################################################

def remove_0tier_stars(star_list, SM_worlds):
    
    #remove stars from the list that have a t0 tier! I do not want these buggers lingering indefinitely!
    active_list = [entry for entry in star_list if int(approximate_current_tier(entry['call_time'],entry['tier'])) != 0]    
    #also must remove any stars that have, according to SM, poofed. we can remove those stars manually using $poof command; however, if we are instead automating the $active loop and have nobody actively removing poofed stars, I would like the list to cleanse itself -- like a cat.
    
    #if star in $active list has (SM) in the username variable name AND the star's world is not in the updated SM_worlds list, remove that star. Scrub-a-dub-dub
    scrubbed_list = [entry for entry in active_list if not ('(SM)' in entry['username'] and int(entry['world']) not in SM_worlds)]
    
    return scrubbed_list
    
def embed_stars(filename, embed, active=False, hold=False):
    
    #load current list of backup or active stars
    stars = load_json_file(f'keyword_lists/{filename}')

    #pull SM stars from server
    SM_stars = get_SM_f2p_stars()

    #pull list of SM worlds (will need later)
    SM_worlds = [int(sm_star['world']) for sm_star in SM_stars]

    if active:

        #REMOVE STARS WITH TIER 0* and poofed stars (i.e., stars in our $active list which are not in SM updated list)
        updated_stars = remove_0tier_stars(stars, SM_worlds)       

        #add SM stars to list of active stars. will also calibrate the tiers with the SM calls!
        updated_stars = add_SM_to_active(updated_stars, SM_stars)

        #re-save active_stars.json file
        save_json_file(updated_stars, f'keyword_lists/{filename}')
    
    #if "hold," then remove ANY stars from $backups list if that star appears in the SM list of active stars
    else:
        #check if any SM active stars are in our backups list. if so, remove from $backups.
        updated_stars = calibrate_backups(SM_stars, stars)
                
        #re-save file
        save_json_file(updated_stars, f'keyword_lists/{filename}')
    
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
            
            #just a quick check to monitor cases where tiers don't match the Star Miners plugin
            #this will also indicate whether I should be using approx or star['world']
            if int(star['world']) in SM_worlds:
                sm_tier = int(star['tier'])
                approx = approximate_current_tier(call_time, sm_tier)
                if approx != sm_tier:
                    print(f"📉 Tier shift detected: SM = {sm_tier}, now = {approx}, world = {star['world']}")
            
            current_tier = approximate_current_tier(call_time, star['tier']) if int(star['world']) not in SM_worlds else star['tier']
            
            #get time remaining (in seconds) for the star! use the "current tier" above!
            time_remaining = get_time_remaining(call_time, current_tier)
            
            embed.add_field(
                    name=f'⭐ Star {i+1} ⭐',
                    value=f'{star['world']} {star_full_loc} [{star_loc}] Tier {current_tier}*\nDust time: <t:{time_remaining}:R>\nCalled by: {star['username']}',
                    inline=False
                )
        if hold:
            embed.add_field(
                name=f'⭐ Star {i+1} ⭐',
                value=f'{star['world']} {star_full_loc} [{star_loc}] Tier {star['tier']} -- {star['username']}',
                inline=False
            )

    #add 'Updated/posted [xx minutes ago]'
    timestamp=int(time.time())
    embed.add_field(name="\u200b", value=f"Posted/last updated <t:{timestamp}:R>", inline=False)
            
    return embed

def approximate_current_tier(call_time, original_tier):
    #max(a,b) --> gives the larger of a and b. 
    #returns current tier of the star, given the original call time (when set to $active)
    original_tier = int(original_tier)   #ensuring integer, not string or float
    current_tier = max(0, original_tier - int((time.time() - call_time) / (7 * 60)))
    return current_tier

#get time remaining (in seconds) for the star!
def get_time_remaining(call_time, original_tier):
    original_tier = int(original_tier)
    time_since_call = time.time() - call_time
    star_dust_time = int(original_tier)*7*60   #take original tier, convert to seconds expected to last
    time_remaining = star_dust_time - time_since_call   #time remaining until star dusts
    time_remaining = int(time.time() + time_remaining)   #convert to Unix time
    
    return time_remaining


