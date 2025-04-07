import requests
import json

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
    with open("keyword_lists/encouragement.txt", "w") as f:
        f.write("\n".join(keywords))
        
#load list of encouragement keywords        
def load_encouragement_keywords():
    try:
        with open("keyword_lists/encouragement.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print('keyword_lists/encouragement.txt file not found; loading default list instead.')
        return ['Keep doing your best','Just keep swimming','One moment at a time',
                'Save those tears for your pillow','Cheer up','Absorb some sunshine',
                'Any worthwhile endeavor will take time and patience']

    
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
    loc_dict = load_loc_dict()
    loc_shorthand = message.content[5:].strip()     #removes '$loc ' from string
    try:
        return loc_shorthand, loc_dict[loc_shorthand]
    except:
        return 'Location invalid! See https://locations.dust.wiki for a list of our shorthand.'