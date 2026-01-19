# ALL OF THE FUNCTIONS WHICH INVOLVE PULLING FROM GOOGLE SHEETS (dust.wiki) ARE ADDED HERE

import gspread
from google.oauth2.service_account import Credentials
import numpy as np
import json
import time
import asyncio

from universal_utils import remove_frontal_corTex, load_f2p_worlds, load_json_file
    
#TIER 6 -- B, TIER 7 -- C, TIER 8 -- D, TIER 9 -- E
#star tier index for "Suggested EOW Call Times" sheet on dust.wiki
tier_dict = {'6':'B', '7':'C', '8':'D', '9':'E'}

#this the dict indicating when in the wave to call a star if there is no poof data!
#the tier 6 is a bit tricky - I do default to +91 here, though it should be ~+3 into the new wave. 
tier_call_dict = {'6':'91', '7':'87', '8':'81', '9':'75'}


#GET SPREADSHEET after inserting credentials
def open_spreadsheet(retries=3, delay=10):
    '''
    Open the Google Sheet.

    Args:
        retries (int): Number of times to retry if the request fails.
        delay (int): Seconds to wait between retries.

    Returns:
        gspread.Spreadsheet: The opened spreadsheet object, or raises Exception if it fails.
    '''
    ###SERVICE ACCOUNT SETUP###
    scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file('config/animated-scope-456121-q8-5b10debc616d.json', 
                                                             scopes=scopes)

    ###OPEN SPREADSHEET WITH RETRIES###
    for attempt in range(retries):
        try:
            gc = gspread.authorize(creds)
            spreadsheet = gc.open_by_key('17rGbgylW_IPQHaHUW1WsJAhuWI7y2WhplQR79g-obqg')
            return spreadsheet
        except Exception as e:
            print(f"[open_spreadsheet] Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)  #wait before retrying
            else:
                raise  #only raise after final attempt


#ASYNC version of get_wave_time
async def get_wave_time():
    '''
    Pulls current wave time from dust.wiki Dashboard!C3
    Returns a string value (e.g. '14').
    '''
    spreadsheet = await asyncio.to_thread(open_spreadsheet)
    wave_time = await asyncio.to_thread(spreadsheet.worksheet('Dashboard').get, 'C3')
    return wave_time[0][0]


#ASYNC returns Unix epoch-converted start and end wave times
async def get_wave_start_end():
    '''
    Returns Unix epoch start and end times of the wave, along with minutes elapsed.
    '''
    wave_time = int(await get_wave_time()) * 60  #minutes converted to seconds
    current_time = time.time()                   #Unix epoch time
    
    sec_until_eow = 92*60 - wave_time
    wave_start_time = int(current_time - wave_time)
    wave_end_time = int(current_time + sec_until_eow)
        
    return wave_start_time, wave_end_time, int(wave_time/60)


#read and parse list of f2p worlds in all_f2p_worlds.txt
#NOTE: start and end indices are the first and last cell indices in the column
#outputs a dictionary of worlds and their corresponding cell index in the Google Sheet
def parse_world_list(start_index, end_index):
    _, world_list = load_f2p_worlds(output_all_worlds=True)
    
    #poof times on dust.wiki are in cells B5:65 ('Spawn Time Estimates')
    possible_cells = np.arange(start_index, end_index+1, 1)
    
    #creates a dictionary that will return the cell number of the world
    world_dict = dict(zip(world_list, possible_cells))
    
    return world_dict


#ASYNC function to pull poof time for given F2P world from dust.wiki
async def get_poof_time(world_string):
    '''
    Pulls poof time for a given F2P world.
    Returns a string (minutes) or 'TBD'.
    '''
    if world_string not in load_f2p_worlds():
        return 'Try again, and maybe use a valid F2P world this time.'
    
    world_dict = parse_world_list(5, 65)
    cell_index = world_dict[world_string]
    cell = 'B' + str(cell_index)
    
    spreadsheet = await asyncio.to_thread(open_spreadsheet)
    try:
        poof_time = await asyncio.to_thread(spreadsheet.worksheet('Spawn Time Estimates').get, cell)
        return poof_time[0][0]
    except:
        return 'TBD'


#ASYNC from the appropriate cell for the appropriate world, pull the call time
async def get_call_time(world_string, tier_string):
    '''
    Pulls suggested call time for given F2P world/tier.
    Returns a string (e.g. '+20', '20')
    '''
    spreadsheet = await asyncio.to_thread(open_spreadsheet)
            
    world_dict = parse_world_list(3, 63)
    column_index = tier_dict[str(tier_string)]
    world_index = world_dict[world_string]
    cell = str(column_index) + str(world_index)
    
    try:
        call_time = await asyncio.to_thread(spreadsheet.worksheet('Suggested EOW Call Times').get, cell)
        return call_time[0][0]
    
    except:   #cell is empty, default to the times given in the global dictionary -- tier_call_dict
        return tier_call_dict[str(tier_string)]


#################################################
# CONVERT CALL TIME OF STAR TO UNIX TIME #
# RETURNS UNIX EPOCH TIME FOR WHEN TO CALL STAR #
#################################################
async def get_call_time_unix(world_string, tier_string, call_time, wave_time):
    
    #grab the suggested call time for the star
    if call_time is None:
        call_time = await get_call_time(world_string, tier_string)
    
    #grab the current wave time
    if wave_time is None:
        wave_time = await get_wave_time()
    
    #determine the minutes remaining in the wave until time to call star
    minutes_until_call = int(call_time.replace('+','')) - int(wave_time)
    
    #convert minutes to seconds in order to add to unix epoch time correctly
    seconds_until_call = minutes_until_call * 60

    #grab the unix epoch time, in seconds
    current_time_seconds = time.time()

    #calculate the time to call, now in unix-ready format
    time_to_call_unix = int(current_time_seconds + seconds_until_call)
    
    return time_to_call_unix
       
##################################################################
# ASYNC check whether the star is callable; returns a bool flag! #
##################################################################
async def check_wave_call(world, tier, wave_time=None, call_time=None):
    
    try:
        if wave_time is None:
            wave_time = await get_wave_time()
        wave_time = int(wave_time)    
            
        if call_time is None:
            
            #if the tier is < 6...default to +85 call time.
            call_time = '+85' if (int(tier) < 6) else await get_call_time(world, tier)
        
        call_time = int(call_time.replace('+',''))

        return wave_time > call_time
    
    except Exception as e:
        print('check_wave_call() error:',e)


#ASYNC function to get the list of F2P worlds in order of early-to-late poof times. 
#worlds with no poof times are defaulted to the end of the list
async def get_ordered_worlds():
    spreadsheet = await asyncio.to_thread(open_spreadsheet)
    worksheet = spreadsheet.worksheet('Spawn Time Estimates')
    
    cell_list = await asyncio.to_thread(worksheet.get, 'K5:K64')
    worlds = [row[0][:3] for row in cell_list if row]
    
    f2p_worlds_list = load_f2p_worlds()
    worlds_updated = [int(world) for world in worlds if str(world) in f2p_worlds_list]
    
    worlds_updated = str(worlds_updated).replace("[","").replace("]","").replace(" ","")
    return worlds_updated
