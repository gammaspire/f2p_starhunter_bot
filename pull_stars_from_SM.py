#need to pull stars from SM and add to $active embed
#most important is to check world
#if world entry is already in $active, either ignore or replace with SM entry

import requests
from universal_functions import world_check_flag, load_json_file, save_json_file


#extract list of Star Miners F2P active stars
def get_SM_f2p_stars():
    
    #url where star data is stored
    sm_url = 'https://map.starminers.site/data2'

    #load list of F2P worlds
    with open('keyword_lists/f2p_worlds.txt', 'r') as file:   #read in file
        lines = file.readlines()                              #grab all lines (one world per line)
    
    #convert to list; if ttl world, then the length will be >3 characters; truncate to just
    #3 characters so fits better with the syntax of the discord command I'm setting up
    world_list = [line.strip()[0:3] for line in lines] 
    
    try:
        response = requests.get(sm_url,timeout=10)   #will time out after 10 seconds
        response.raise_for_status()  #raises an error for bad responses (like 500 or 404)
        
        data = response.json()
    
        #grab list of f2p stars from SM
        f2p_stars = [entry for entry in data if str(entry['world']) in world_list]
    
    #adding a couple of failsafes...
    except requests.exceptions.RequestException as e:
        print(f"[SM FETCH ERROR] Failed to fetch F2P stars: {e}")
        return []
    except ValueError as e:
        print(f"[SM JSON ERROR] Invalid JSON from SM: {e}")
        return []
    
    return f2p_stars
      

#add Star Miners stars to our $active list, replace stars called using $call with SM counterparts, if they exist
def add_SM_to_active(our_active_stars, SM_stars):

    #convert list of our_active_stars to a dictionary {world: star}
    active_by_world = {str(star['world']): star for star in our_active_stars}

    for SM_star in SM_stars:
        
        #grab the world of the SM star
        world_key = str(SM_star['world'])

        #replace or add the SM star
        active_by_world[world_key] = {
            "username": f"{SM_star['calledBy']} (SM)",
            "user_id": "None",
            "world": world_key,
            "loc": SM_star['calledLocation'],
            "tier": str(SM_star['tier']),
            "call_time": int(SM_star['calledAt'])
        }

    #convert back to list of stars!
    return list(active_by_world.values())

    
#check if SM star is in our $backups list. if so, remove from $backups.        
def calibrate_backups(SM_f2p_stars, backup_stars):
    #there are not too many f2p stars...not concerned about optimizing the comparisons here
    
    #create list of f2p worlds with active SM stars
    SM_f2p_star_worlds = []
    
    #for every star, isolate str(world) and add to list
    for SM_star in SM_f2p_stars:
        world = str(SM_star['world'])
        SM_f2p_star_worlds.append(world)
    
    #update the backups stars...only keep stars whose worlds are NOT in the SM_f2p_star_worlds list!
    updated_backup_stars = [entry for entry in backup_stars if str(entry['world']) not in SM_f2p_star_worlds]
    
    return updated_backup_stars
    