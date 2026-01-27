#an array of functions used for calling stars; independent of but works in 
#conjunction with the googlesheets_utils.py functions

import requests
import json
import os
import random
import time

from universal_utils import *
from SM_utils import *

    
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
def add_star_to_list(username, user_id, world, loc, tier, 
                     call_time_unix=None, poof_time=None, filename='held_stars.json'):

    #grab time at which star is added to list --> will use to determine star tier later on
    time_added = time.time()

    #isolate the tier number in case someone entered t# or T#
    tier = remove_frontal_corTex(tier)

    stars_list = load_json_file(f'keyword_lists/{filename}')

    #if star is active, time_to_call is irrelevant. similarly, if star is hold then poof_estimate is irrelevant. 
    #otherwise, assign the "time to call" or "poof estimate" variable to the unix epoch time 
    #fed into the function
    time_to_call='N/A'
    if "held" in filename:
        time_to_call = call_time_unix
        
    stars_list.append({
        "username": username,
        "user_id": user_id,
        "world": world,
        "loc": loc,
        "tier": tier,
        "call_time": time_added,
        "time_to_call": time_to_call,
        "poof_estimate": poof_time
    })

    with open(f'keyword_lists/{filename}','w') as f:
        json.dump(stars_list, f, indent=6)   #indent indicates number of entries per array?

def print_error_message(command):
    message = f"Missing or invalid arguments!\n- Syntax: ${command} world loc tier\n- World should be F2P, loc must be one of our shorthand keys, and the tier SHOULD be 6-9 for held star or 1-9 for active star.\n- Example: ${command} 308 akm 8"
    return message
   
    
############################################################
#remove star from held_stars.json ($remove_held) OR active_stars.json ($poof)
#use: 
#   $remove world
#   $poof world
#e.g., 
#   $remove 308
#   $poof 308
############################################################
        
def remove_star(world,filename='held_stars.json',output_data=False):

    #remove star from the .json
    all_held_stars = load_json_file(f'keyword_lists/{filename}')
    
    #if output_data needed for the $remove command (meaning that the command returns the Loc and Tier associated with the star), grab that information and assign to variables
    if output_data:
        #creating variable placeers...just in case
        loc=None
        tier=None
        for n in all_held_stars:
            if str(n['world'])==str(world):
                loc=n['loc']
                tier=n['tier']
    
    #the WORLD is the only unique identifier for every entry -- remove entry corresponding to world!
    updated_held_stars = [entry for entry in all_held_stars if str(entry["world"]) != str(world)]
    
    save_json_file(updated_held_stars, f'keyword_lists/{filename}')
    
    if output_data:
        if loc is None or tier is None:
            return None, None
        return loc, tier


############################################################
#Star Management Utils
#used primarily for management of the embed active/backup lists!
############################################################       
    
def remove_0tier_stars(star_list, SM_worlds):
    '''
    AIM: remove stars from the list that have a t0 tier! I do not want these buggers lingering indefinitely!
         also must remove any stars that have, according to SM, poofed. we can remove those stars manually using $poof command; however, if we are instead automating the $active loop and have nobody actively removing poofed stars, I would like the list to cleanse itself -- like a cat.
    '''
    active_list = [entry for entry in star_list if int(approximate_current_tier(entry['call_time'],entry['tier'])) != 0]    
    
    #if star in $active list has (SM) in the username variable name AND the star's world is not in the updated SM_worlds list, remove that star. Scrub-a-dub-dub
    scrubbed_list = [entry for entry in active_list if not ('(SM)' in entry['username'] and int(entry['world']) not in SM_worlds)]
    
    return scrubbed_list


def remove_old_stars(star_list, cutoff=7200):
    '''
    AIM: scrub the held stars list of backups that have lingered for > cutoff (seconds).
    Every star has a call_time, which, contrary to what the variable name hints, is NOT the time 
        at which the star must be called. instead, it is the time at which the user held the star.
    '''
    
    #get current time
    current_time = time.time()
    
    scrubbed_list = [entry for entry in star_list if ((current_time - int(entry['call_time']) < cutoff))]
    dirty_list = [entry['world'] for entry in star_list if ((current_time - int(entry['call_time']) > cutoff))]
    
    if len(dirty_list) != 0:
        print(f'Removing backup star for world(s) {dirty_list} -- no longer valid.')
    
    return scrubbed_list


def get_clean_backups():
    '''
    AIM: REMOVE EXPIRED BACKUP STARS FROM THE BACKUPS LIST!
    '''
    backups = load_json_file('keyword_lists/held_stars.json')
    backups = remove_old_stars(backups)
    save_json_file(backups, 'keyword_lists/held_stars.json')
    return backups


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