import requests
import json
import os
import random


############################################################
#print a random joke, courtesy of our own tj44
#use: 
#   e.g., $joke
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
#pulls randomly-generated random fact
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
#   $add_inspo [your encouraging message here]
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
        return ['Keep doing your best.','Just keep swimming.','One moment at a time.',
                'Save those tears for your pillow.','Cheer up.','Absorb some sunshine.',
                'Any worthwhile endeavor will take time and patience.','sarcasm']

def load_sad_keywords():
    try:
        with open("keyword_lists/sad_keywords.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print('keyword_lists/sad_keywords.txt file not found; loading default list instead.')
        return ['miserable','sad','unhappy','sadgams','angry','upset','depressed','infuriated','grumpy']

def sarcastify_word(word):
    if word=='D:':
        return word
    string=''
    for n in range(len(word)):
        string+=word[n].lower() if n%2==0 else word[n].upper()
    return string
    
################################################
#ask the magic conch shell to resolve your indecision.
#use: 
#   $conch
################################################
def load_conch_responses():
    
    try:
        with open("keyword_lists/conch.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print('keyword_lists/conch.txt file not found; loading default list instead.')
        return ['Yes.','No.','Maybe.']

################################################
#disagree? VOCALIZE YOUR DISAPPROVAL HERE!
#use: 
#   $strike
################################################    
def load_protests():
    
    try:
        with open("keyword_lists/strike.txt", "r") as f:
            return [line.strip().replace("\\n", "\n") for line in f if line.strip()]
    except FileNotFoundError:
        print('keyword_lists/protest.txt file not found; loading default list instead.')
        return ['No.','Ask somebody else!']
    
