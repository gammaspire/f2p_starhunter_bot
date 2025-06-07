import json

#to reactivate any scheduled jobs, must first grab job IDs
def grab_job_ids(job_info):            
    channel_id = job_info['channel_id']
    interval = job_info['interval']        
    return channel_id, interval

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

#remove any T prefixes 
def remove_frontal_corTex(tier_string):
    try:
        if (tier_string[0]=='t') | (tier_string[0]=='T'):
            return tier_string[1]
        return tier_string
    except TypeError:
        return None

#read in list of F2P Worlds
def load_f2p_worlds():
    
    with open('keyword_lists/f2p_worlds.txt', 'r') as file:   #read in file
        lines = file.readlines()                              #grab all lines (one world per line)

    #convert to list; if ttl world, then the length will be >3 characters; truncate to just
    #3 characters so fits better with the syntax of the discord command I'm setting up
    world_list = [line.strip()[0:3] for line in lines] 

    return world_list

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

