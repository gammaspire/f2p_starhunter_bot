import json
import os


#to reactivate any scheduled jobs, must first grab job IDs
def grab_job_ids(job_info):            
    channel_id = job_info['channel_id']
    interval = job_info['interval'] 
    message_id = job_info.get('message_id')       
    return channel_id, interval, message_id


def load_json_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

    
#this will write job to filename, and create filename if does not already exist
def save_json_file(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f)

        
#remove any T prefixes 
def remove_frontal_corTex(tier_string):
    try:
        if (tier_string[0]=='t') | (tier_string[0]=='T'):
            return tier_string[1]
        return tier_string
    except TypeError:
        return None

    
#read in list of currently active F2P Worlds
def load_f2p_worlds(output_omitted_worlds = False, output_all_worlds = False):
    
    active_path = os.path.join('keyword_lists', 'active_f2p_worlds.txt')
    all_path = os.path.join('keyword_lists', 'all_f2p_worlds.txt')
    
    #contains list of active worlds which may be < all_f2p_worlds.txt, either due to temporary server outages 
    #or the (temporary..?) conversion of the world to P2P-only.
    with open(active_path, 'r', encoding="utf-8") as file:   #read in file
        lines_active = file.readlines()                              #grab all lines (one world per line)

    #also load the omit_worlds.txt file! 
    #contains list of worlds to omit from the F2P list, either due to temporary server outages 
    #or the (temporary..?) conversion of the world to P2P-only.
    with open(all_path, 'r', encoding="utf-8") as file:   #read in file
        lines_all = file.readlines()                              #grab all lines (one world per line)

    #if ttl world, then the length will be >3 characters; truncate to just
    #3 characters so fits better with the syntax of the discord command I'm setting up
    active_worlds = list(str(line.strip()[0:3]) for line in lines_active)

    if output_all_worlds:
        all_worlds = [line.strip()[0:3] for line in lines_all]
        return active_worlds, all_worlds
    
    if output_omitted_worlds:
        omitted_worlds = [line.strip()[0:3] for line in lines_all if str(line.strip()[0:3]) not in active_worlds]
        
        print('List of current ex-F2P worlds:')
        print(omitted_worlds)
        
        return active_worlds, omitted_worlds
    
    return active_worlds


#check whether world is already in filename (either held_stars.json or active_stars.json)
def world_check_flag(world, filename=None, active_stars=None):
    
    if filename!=None:
        stars = load_json_file(f'keyword_lists/{filename}')
    else:
        stars = active_stars
    
    #if true, an entry with the given world is already registered in the .json file
    #note that SM worlds are integers
    world_flag = (any(str(entry["world"]) == str(world) for entry in stars)) | \
                 (any(int(entry["world"]) == int(world) for entry in stars))
    
    return world_flag


def get_star_holder(world: str, filename="held_stars.json"):
    stars = load_json_file(f'keyword_lists/{filename}') or []
    for s in stars:
        if str(s.get("world")) == str(world):
            return s
    print('I anticipate a problem stemming from universal_utils/get_star_holder might be imminent...')
    return None


######################################################
# LOAD THE POOF CACHE (DICTIONARY {WORLD:POOF_TIME}) #
######################################################

def load_poof_cache():
    poof_cache = load_json_file('keyword_lists/poofdata_cache.json')
    return poof_cache

def fetch_poof(poof_cache, world: str):
    '''
    Easily grab poof time from the poofdata_cache.json file.
    '''
    poof_time = poof_cache[world]
    return poof_time