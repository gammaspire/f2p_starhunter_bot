# ALL OF THE FUNCTIONS WHICH INVOLVE PULLING FROM GOOGLE SHEETS (dust.wiki) ARE ADDED HERE

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import numpy as np
import json
import time
from universal_functions import remove_frontal_corTex, load_f2p_worlds, load_json_file
    
    
#TIER 6 -- B, TIER 7 -- C, TIER 8 -- D, TIER 9 -- E
#star tier index for "Suggested EOW Call Times" sheet on dust.wiki
tier_dict = {'6':'B', '7':'C', '8':'D', '9':'E'}


#GET SPREADSHEET after inserting credentials
def open_spreadsheet():
    #scope grants access to read/write spreadsheets and access Google Drive for sharing
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name('animated-scope-456121-q8-5b10debc616d.json', scope)
    gc = gspread.authorize(creds)

    #open Google Sheet (you can also use .worksheet("Tab Name"))
    #key is part of dust.wiki hyperlink...which is public
    spreadsheet=gc.open_by_key('17rGbgylW_IPQHaHUW1WsJAhuWI7y2WhplQR79g-obqg')
    
    return spreadsheet


#function that will pull the current wave time from dust.wiki
def get_wave_time():
    
    spreadsheet = open_spreadsheet()

    #prints cell C3, giving the number of minutes until EoW
    #returns a nested list (e.g., [['14']]...so [['14']][0][0] yields '14'). I do not make the rules.
    
    wave_time = spreadsheet.worksheet('Dashboard').get('C3')[0][0]
    
    return wave_time


#returns Unix epoch-converted start and end wave times
def get_wave_start_end():
    wave_time = int(get_wave_time())*60  #minutes converted to seconds
    current_time = time.time()           #Unix epoch time...number of seconds since 
                                         #January 1, 1970 (midnight UTC/GMT)
    
    sec_until_eow = 92*60 - wave_time
    
    wave_start_time = int(current_time - wave_time)
    wave_end_time = int(current_time + sec_until_eow)
        
    return wave_start_time, wave_end_time, int(wave_time/60)


#read and parse list of f2p worlds in f2p_worlds.txt
#NOTE: start and end indices are the first and last cell indices in the column
#outputs a dictionary of worlds and their corresponding cell index in the Google Sheet
def parse_world_list(start_index, end_index):
    #open txtfile
    with open('keyword_lists/f2p_worlds.txt', 'r') as file:   #read in file
        lines = file.readlines()                              #grab all lines (one world per line)
    
    #convert to list; if ttl world, then the length will be >3 characters; truncate to just
    #3 characters so fits better with the syntax of the discord command I'm setting up
    world_list = [line.strip()[0:3] for line in lines] 
    
    #poof times on dust.wiki are in cells B5:65 ('Spawn Time Estimates')
    possible_cells = np.arange(start_index,end_index+1,1)   #add 1 to end_index because *python*
    
    #creates a dictionary that will return the cell number of the world
    world_dict = dict(zip(world_list,possible_cells))
    
    return world_dict

#function to pull poof time for given F2P world from dust.wiki
def get_poof_time(world_string):
    
    if world_string not in load_f2p_worlds():
        return 'Try again, and maybe use a valid F2P world this time.'
    
    world_dict = parse_world_list(5,65)

    cell_index = world_dict[world_string]
    cell = 'B'+str(cell_index)

    spreadsheet = open_spreadsheet()
    
    try:
        poof_time = spreadsheet.worksheet('Spawn Time Estimates').get(cell)[0][0]
    except:
        poof_time = 'TBD'
    
    return poof_time
    
#pull wave time and poof time for world. if world is recognized in the f2p world list, then
#print the poof time for the world, the current wave time, and whether the star is callable.
#otherwise, the print message will a default "World unknown", etc.
def create_poof_message(world_string):
    
    if world_string not in load_f2p_worlds():
        return 'Error, likely because you are not using a valid F2P world. What a maroon.'
    
    poof_time = get_poof_time(world_string)

    #prints poof time for world and current wave time.

    if poof_time=='TBD':
        return f'Poof time for {world_string} is {poof_time}!'
    else:
        wave_time = get_wave_time()
        return f'Poof time for {world_string} is +{poof_time}. The current wave time is +{wave_time}.'
    

#from the appropriate cell for the appropriate world, pull the call time
def get_call_time(world_string, tier_string):
    
    spreadsheet = open_spreadsheet()
            
    #cells for poof times are from 3 to 63
    #this dictionary will connect world numbers with their cell index
    world_dict = parse_world_list(3,63)
    
    column_index = tier_dict[str(tier_string)]
        
    world_index = world_dict[world_string]
    
    cell = str(column_index)+str(world_index)
    
    #call time is from the cell ONLY if the poof data exists
    try:
        call_time = spreadsheet.worksheet('Suggested EOW Call Times').get(cell)[0][0]

    except:
        call_time = '*85*'    
    
    return call_time
    
def create_eow_message(world_string, tier_string):
    
    #remove any t or T prefix
    tier_string = remove_frontal_corTex(tier_string)
    
    #TIER 6 -- B, TIER 7 -- C, TIER 8 -- D, TIER 9 -- E        
    #if tier is not one of the default 4, wir haben einen Problem. 
    if int(tier_string) not in [6,7,8,9]:
        return 'Tier must be 6, 7, 8, or 9. Please and thank you.'
    
    #also...if world not found, or f2p world is temporarily a p2p world, toss this error to the user
    if world_string not in load_f2p_worlds():
        return 'Use a valid F2P world!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! It is not that difficult, I promise.'
    
    
    #otherwise...prints call time for world and current wave time.
        
    try:
        
        call_time = get_call_time(world_string,tier_string)
                
        #if the call time is *85*, then we do not yet have poof data for that world
        #for the purposes of collecting poof data, hold star until +85 unless backup is needed immediately
        if call_time=='*85*':
            return f'Poof data for {world_string} is TBD. Please default to holding until +85 into the wave.' 
        else:
            wave_time = get_wave_time()
            
            #call_time in the cell is +xx, so remove + to convert to integer
            #otherwise...please hold the star. :-)  
            if int(wave_time)<int(call_time.replace('+','')):
                call_notice = f'Please hold for {int(call_time.replace('+',''))-int(wave_time)} minutes.'
            #if the wave time is larger than the call time, then I can call the star! 
            else:
                call_notice = f'You can call the star now!'

            return f'The suggested call time for {world_string} T{tier_string} is {call_time}. The current wave time is +{wave_time}. {call_notice}'
    
    #otherwise...prints call time for world and current wave time.
    except:
        return f"For Pete's sake, PLEASE use a valid F2P world."

    
#check whether the star is callable; returns a bool flag!
def check_wave_call(world,tier):
    wave_time = int(get_wave_time())
    call_time = get_call_time(world,tier)
    
    #if poof time is unknown, default call time to +85 into the wave
    if call_time=='*85*':
        call_time=85
    else:
        call_time = int(call_time.replace('+',''))
    
    #if can call star, TRUE
    if wave_time>call_time:
        return True
    #if can't call star, FALSE
    if wave_time<call_time:
        return False
    

#function to get the list of F2P worlds in order of early-to-late poof times. 
#worlds with no poof times are defaulted to the end of the list
def get_ordered_worlds():

    spreadsheet = open_spreadsheet()

    #now...grab the list of cells
    worksheet = spreadsheet.worksheet('Spawn Time Estimates')

    #get cell list from indices corresponding to the world cells in the Spawn Time Estimates Google Sheet
    cell_list = worksheet.get('K5:K64')

    #convert to a comma-separated python list of world strings, the "if row" is a failsafe against potential empty cells
    worlds = [row[0][:3] for row in cell_list if row]

    #pull list of f2p worlds, which factors in any worlds which may have been converted to p2p worlds
    #note that this requires maintenance of omit_worlds.txt
    f2p_worlds_list = load_f2p_worlds()

    #finally, filter out any worlds which do not appear in the full f2p list!
    worlds_updated = [int(world) for world in worlds if str(world) in f2p_worlds_list]

    #convert list into a full string
    worlds_updated = str(worlds_updated)
    
    #replace the silly brackets
    worlds_updated = worlds_updated.replace("[", "")
    worlds_updated = worlds_updated.replace("]", "")
    
    #replace the silly spaces
    worlds_updated = worlds_updated.replace(" ", "")
    
    return worlds_updated


#generate the actual "hoplist" text for when I send the $hoplist message
def generate_hoplist_text():
    worlds = get_ordered_worlds()  
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
    
    full_text = "Here is a filtered list of worlds in order of early- to late-wave spawns. The list is formatted so that you can directly Copy+Paste the text into the World Cycle Runelite plugin!\n\n" + worlds + '\n\n' + f'-# Posted/last updated <t:{timestamp}:R>'
    
              
    return full_text
