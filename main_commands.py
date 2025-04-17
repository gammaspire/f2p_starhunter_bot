import requests
import json
import os
import random

#remove any T prefixes 
def remove_frontal_corTex(tier_string):
    if (tier_string[0]=='t') | (tier_string[0]=='T'):
        return tier_string[1]
    return tier_string

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
def add_held_star(username,user_id,world,loc,tier,filename='held_stars.json'):
        
    #isolate the tier number in case someone entered t# or T#
    tier = remove_frontal_corTex(tier)
    
    held_stars = load_json_file(f'keyword_lists/{filename}')
    
    #if an entry with the same f2p world is not already in the .json file, add it!
    world_check = world_check_flag(world, filename)
    
    if not world_check:    
        
        held_stars.append({
            "username": username,
            "user_id": user_id,
            "world": world,
            "loc": loc,
            "tier": tier
        })
    
    with open(f'keyword_lists/{filename}','w') as f:
        json.dump(held_stars, f, indent=5)   #indent indicates number of entries per array?

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
#hold star in held_stars.json file until time to release
#use: 
#   $backups
############################################################
def embed_backups(filename, embed):
    
    held_stars = load_json_file(f'keyword_lists/{filename}')
    
    #load location dictionary
    loc_dict = load_loc_dict()
    
    for i,star in enumerate(held_stars):
        star_loc = star['loc']
        try:
            star_full_loc = loc_dict[star_loc]
        except:
            star_full_loc = star_loc
        embed.add_field(
            name=f'⭐ Star {i} ⭐',
            value=f'{star['world']} {star_full_loc} t{star['tier']} - {star['username']}',
            inline=False
        )
        
    return embed
