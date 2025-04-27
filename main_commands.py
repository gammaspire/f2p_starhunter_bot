import requests
import json
import os
import random
import time

#remove any T prefixes 
def remove_frontal_corTex(tier_string):
    try:
        if (tier_string[0]=='t') | (tier_string[0]=='T'):
            return tier_string[1]
        return tier_string
    except TypeError:
        return None
        
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
#load json file which holds all scheduled jobs
#save json file with updated scheduled jobs
#from json file, grab IDs
############################################################
def load_json_file(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

#this will write job to filename, and create filename if does not already exist
def save_json_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)
        
#to reactivate any scheduled jobs, must first grab job IDs
def grab_job_ids(job_info):            
    channel_id = job_info['channel_id']
    interval = job_info['interval']        
    return channel_id, interval



############################################################
#hold star in held_stars.json file until time to release
#use: 
#   $hold world loc tier
#e.g., 
#   $hold 308 nc 8
############################################################

def world_check_flag(world, filename):
    
    held_stars = load_json_file(f'keyword_lists/{filename}')

    #if true, an entry with the given world is already registered in the .json file
    world_check_flag = any(entry.get("world") == str(world) for entry in held_stars)

    return world_check_flag
    

#using JSON file --> a convenient approach to storing dictionary keys. :-)
def add_star_to_list(username,user_id,world,loc,tier,filename='held_stars.json'):
        
    
    #if an entry with the same f2p world is not already in the .json file, add it!
    world_check = world_check_flag(world, filename)
    
    if not world_check:    
        
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
    message = 'Missing or invalid arguments!\nSyntax: $hold world loc tier\nWorld should be F2P, loc must be one of our shorthand keys, and the tier must be 6-9\nExample: $hold 308 akm 8'
    return message
        
############################################################
#remove star from held_stars.json
#use: 
#   $remove world
#e.g., 
#   $remove 308
############################################################
        
def remove_held_star(world,filename='held_stars.json',output_data=False):
    #remove star from the .json
    all_held_stars = load_json_file(f'keyword_lists/{filename}')
    
    #if output_data needed for the $remove command...
    if output_data:
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
def embed_stars(filename, embed, active=False, hold=False):
    
    stars = load_json_file(f'keyword_lists/{filename}')
    
    if active:
        
        #REMOVE STARS WITH TIER 0* (then re-save file)
        updated_stars = [entry for entry in stars if int(get_current_tier(entry['call_time'],entry['tier'])) != 0]
        save_json_file(updated_stars, f'keyword_lists/{filename}')
    
    else:
        updated_stars=stars
    
    #load location dictionary
    loc_dict = load_loc_dict()
    
    for i,star in enumerate(updated_stars):
        
        call_time = int(star['call_time'])
        star_loc = star['loc']
        
        try:
            star_full_loc = loc_dict[star_loc]
        except:
            star_full_loc = star_loc
    
    #if this is the embed for active stars, then include world, loc, current tier when sent, time remaining, and scouter who called the star
        if active:
            #get time remaining (in seconds) for the star!
            time_remaining = get_time_remaining(call_time, star['tier'])
            
            #get current tier for the star
            current_tier = get_current_tier(call_time, star['tier'])
            
            embed.add_field(
                    name=f'⭐ Star {i+1} ⭐',
                    value=f'{star['world']} {star_full_loc} ({star_loc}) Tier {current_tier}*\nDust time: <t:{time_remaining}:R>\nCalled by: {star['username']}',
                    inline=False
                )
        if hold:
            embed.add_field(
                name=f'⭐ Star {i+1} ⭐',
                value=f'{star['world']} {star_full_loc} ({star_loc}) Tier {star['tier']} -- {star['username']}',
                inline=False
            )
    return embed

def get_current_tier(call_time, original_tier):
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


