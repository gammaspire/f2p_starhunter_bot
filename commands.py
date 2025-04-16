import requests
import json
import os
import random


############################################################
#print a random joke, courtesy of our own tj44
#use: 
#   e.g., $haha
#   print randomly-generated TJ joke
############################################################

def load_tj_jokes():
    try:
        with open("keyword_lists/tj_jokes.txt", "r") as f:
            tj_jokes = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print('keyword_lists/tj_jokes.txt file not found; loading default list instead.')
        tj_jokes = ["Did you hear about the bacon that got sick? It was later cured!","Do you know the song 'acne'? It was a breakout hit."]
    return tj_jokes

#will use this function twice for sending a ramdonly-chosen tj44 joke -- once for setting
#up $start_jokes, and once when re-loading all scheduled jobs upon the code's restart!    
async def send_joke(bot, channel_id):
    #get the channel. then post, post, post.
    channel = bot.get_channel(channel_id)
    joke_list = load_tj_jokes()
    chosen_joke = random.choice(joke_list)
    await channel.send(chosen_joke)
        
############################################################
#If message includes any of the keywords, random greeting will print
#use: 
#   e.g., user types "hello bot"
#   bot might respond with "Howdy, {name}!"
############################################################

#storing heaps of keyword lists here...

def pull_greeting_keywords():
    try:
        with open("keyword_lists/greeting_keywords.txt", "r") as f:
            greeting_keywords = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print('keyword_lists/response_greetings.txt file not found; loading default list instead.')
        greeting_keywords = ['hi bot','Hi bot','hello bot','Hello bot','yo bot','Yo bot']    
    
    return greeting_keywords

def greeting_response_keywords():
    
    try:
        with open("keyword_lists/response_greetings.txt", "r") as f:
            common_greetings = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print('keyword_lists/response_greetings.txt file not found; loading default list instead.')
        common_greetings = ['Salutations','Howdy-doo','Welcome']
    
    try:
        with open("keyword_lists/wooly_dislike_list.txt", "r") as f:
            wooly_dislike_list = [line.strip() for line in f if line.strip()] 
    except FileNotFoundError:
        print('keyword_lists/wooly_dislike_list.txt file not found; loading default list instead.')
        wooly_dislike_list = []

    return common_greetings, wooly_dislike_list

################################################
#pulls randomly-generated zen quote 
#result is JSON, so the json module ensures we can more easily work with the data
################################################

def get_zen_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)   #converts API to JSON (I guess)
    quote = json_data[0]['q']+" -"+json_data[0]['a']   #format is from trial and error
    return quote

################################################
#pulls randomly-generated zen quote 
#result is JSON, so the json module ensures we can more easily work with the data
################################################

def get_random_quote():
    response = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random")
    json_data = json.loads(response.text)   #converts API to JSON (I guess)
    quote = json_data["text"]   #format is from trial and error
    return quote

################################################
#add encouraging message to the list of options!
#use: 
#   $add [your encouraging message here]
################################################

def add_encouraging_message(message, keywords):
    new_phrase = message.content[5:].strip()   #remove '$add ' from string
    if new_phrase not in keywords:
        keywords.append(new_phrase)
        flag=True
    else:
        flag=False
    return flag

#save list of encouragement keywords
def save_encouragement_keywords(keywords):
    with open("keyword_lists/response_encouragement.txt", "w") as f:
        f.write("\n".join(keywords))
        
#load list of encouragement keywords        
def load_encouragement_keywords():
    try:
        with open("keyword_lists/response_encouragement.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print('keyword_lists/response_encouragement.txt file not found; loading default list instead.')
        return ['Keep doing your best','Just keep swimming','One moment at a time',
                'Save those tears for your pillow','Cheer up','Absorb some sunshine',
                'Any worthwhile endeavor will take time and patience']

def load_sad_keywords():
    try:
        with open("keyword_lists/sad_keywords.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print('keyword_lists/sad_keywords.txt file not found; loading default list instead.')
        return ['miserable','sad','unhappy','sadgams','angry','upset','depressed','infuriated','grumpy']


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
    return 'Check out out Scouting Guide Here: https://docs.google.com/presentation/d/17bU-vGlOuT0MHBZ9HlTrfQEHKT4wHnBrLTV2_HC8LQU/'

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
#using JSON file --> a convenient approach to storing dictionary keys. :-)
def add_held_star(username,user_id,world,loc,tier,filename='held_stars.json'):
    try:
        with open(f'keyword_lists/{filename}','r') as f:
            held_stars = json.load(f)
    except FileNotFoundError:
        held_stars = []
    
    if (tier[0]=='t') | (tier[0]=='T'):
        tier = tier[1]
    
    held_stars.append({
        "username": username,
        "user_id": user_id,
        "world": world,
        "loc": loc,
        "tier": tier
    })
    
    with open(f'keyword_lists/{filename}','w') as f:
        json.dump(held_stars, f, indent=4)   #indent indicates number of entries per array

def remove_held_star(world,filename='held_stars.json'):
    #remove star from the .json
    all_held_stars = load_json_file(f'keyword_lists/{filename}')
    #the WORLD is the only unique identifier for every entry -- remove entry corresponding to world!
    updated_held_stars = [entry for entry in all_held_stars if entry["world"] != str(world)]
    save_json_file(updated_held_stars, f'keyword_lists/{filename}')
