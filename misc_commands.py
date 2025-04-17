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
