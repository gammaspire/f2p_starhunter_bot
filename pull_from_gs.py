import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import numpy as np

#function that will pull the current wave time from dust.wiki
def get_wave_time():
    #scope grants access to read/write spreadsheets and access Google Drive for sharing
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name('animated-scope-456121-q8-5b10debc616d.json', scope)
    gc = gspread.authorize(creds)

    #open Google Sheet (you can also use .worksheet("Tab Name"))
    #key is part of dust.wiki hyperlink...which is public
    spreadsheet=gc.open_by_key('17rGbgylW_IPQHaHUW1WsJAhuWI7y2WhplQR79g-obqg')

    #prints cell C3, giving the number of minutes until EoW
    #returns a nested list (e.g., [['14']]...so [['14']][0][0] yields '14'). I do not make the rules.
    
    wave_time = spreadsheet.worksheet('Dashboard').get('C3')[0][0]
    
    return wave_time

def create_wave_message():
    wave_time = int(get_wave_time())
    
    if wave_time>45.:
        scout_string='All stars have spawned. Late wave scouting time!'
    elif (wave_time >= 10.) & (wave_time <= 45.):
        scout_string='Begin early-mid scouting now!'
    else:
        scout_string='You can lounge for a bit before scouting.'

    return f"Minutes into Wave: +{wave_time}\nMinutes Until End of Wave: +{92 - wave_time}\n{scout_string}"



#read and parse list of f2p worlds in f2p_worlds.txt
def parse_world_list():
    #open txtfile
    with open('keyword_lists/f2p_worlds.txt', 'r') as file:   #read in file
        lines = file.readlines()                              #grab all lines (one world per line)
    
    #convert to list; if ttl world, then the length will be >3 characters; truncate to just
    #3 characters so fits better with the syntax of the discord command I'm setting up
    world_list = [line.strip()[0:3] for line in lines] 
    
    #poof times on dust.wiki are in cells B5:65 ('Spawn Time Estimates')
    possible_cells = np.arange(5,66,1)
    
    #creates a dictionary that will return the cell number of the world
    world_dict = dict(zip(world_list,possible_cells))
    
    return world_dict

#function to pull poof time for given F2P world from dust.wiki
def get_poof_time(world_string):
    world_dict = parse_world_list()

    cell_index = world_dict[world_string]
    cell = 'B'+str(cell_index)

    #scope grants access to read/write spreadsheets and access Google Drive for sharing
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name('animated-scope-456121-q8-5b10debc616d.json', scope)
    gc = gspread.authorize(creds)

    #open Google Sheet (you can also use .worksheet("Tab Name"))
    #key is part of dust.wiki hyperlink...which is public
    spreadsheet=gc.open_by_key('17rGbgylW_IPQHaHUW1WsJAhuWI7y2WhplQR79g-obqg')
    
    try:
        poof_time = spreadsheet.worksheet('Spawn Time Estimates').get(cell)[0][0]
    except:
        poof_time = 'TBD'
    
    return poof_time
    
#pull wave time and poof time for world. if world is recognized in the f2p world list, then
#print the poof time for the world, the current wave time, and whether the star is callable.
#otherwise, the print message will a default "World unknown", etc.
def create_poof_message(world_string):
    
    try:
        poof_time = get_poof_time(world_string)
        
        #prints poof time for world and current wave time.
        
        if poof_time=='TBD':
            return f'Poof time for {world_string} is {poof_time}!'
        else:
            wave_time = get_wave_time()
            return f'Poof time for {world_string} is +{poof_time}. The current wave time is +{wave_time}.'
    
    except:
        return 'World unknown. Please retry using an F2P world.'
    
    
    
    
    
    
    
