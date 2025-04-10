import requests
import json


############################################################
#If message includes any of the keywords, random greeting will print
#use: 
#   e.g., user types "hello"
#   bot might respond with "uWu, {name}!"
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

    print('hi')
    return common_greetings, wooly_dislike_list

################################################
#pulls randomly-generated zen quote 
#result is JSON, so the json module ensures we can more easily work with the data
################################################

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)   #converts API to JSON (I guess)
    quote = json_data[0]['q']+" -"+json_data[0]['a']   #format is from trial and error
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
    
    

