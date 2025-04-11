import discord
import os
from dotenv import load_dotenv
import random

from commands import *
from pull_from_gs import *

#load environment variables from 'token.env' file
load_dotenv('token.env')

CHANNEL_ID = os.getenv('CHANNEL_ID')   #will need channel ID for later

#define intents; required to read message content in on_message
intents = discord.Intents.default()
intents.message_content = True

#creates client instance
client=discord.Client(intents=intents)

#@client.event is used to register an event. 
@client.event
#the function is called when something happens (in this case, when the discord bot is activated)
async def on_ready():
    print('Logged in as {0.user}'.format(client))

#@client.event is used to register an event.
@client.event
#the function is called when something happens (in this case, when the bot receives message)
async def on_message(message):
    
    #determine name of the user
    name = message.author.display_name
    
    #if the message is from the bot, the bot will not respond...and this function will "exit"
    if message.author == client.user:
        return
        
    ############################################################
    #If message includes any of the keywords, random greeting will print
    #use: 
    #   e.g., user types "hello"
    #   bot might respond with "uWu, {name}!"
    ############################################################
    
    #load greeting keywords 
    greeting_keywords = pull_greeting_keywords()

    if any(word in message.content for word in greeting_keywords):
        
        common_greetings, wooly_dislike_list = greeting_response_keywords()
        
        if name not in wooly_dislike_list:
            chosen_greeting=random.choice(common_greetings)
        else:
            chosen_greeting='Get out'
            
        await message.channel.send(f'{chosen_greeting}, {name}!')
    
    ############################################################
    #If message includes any of the keywords, random encouraging message will print
    #use: 
    #   e.g., user types "I am feeling upset"
    #   bot might respond with "Smile, {name}."
    ############################################################
    sad_keywords = load_sad_keywords()
    if any(word in message.content for word in sad_keywords):
        encouragement = load_encouragement_keywords()   #load list of encouragement phrases!
        chosen_encouragement=random.choice(encouragement)
        await message.channel.send(f'{chosen_encouragement}, {name}.')
    
    ############################################################
    #Print randon inspirational quote
    #use: 
    #   $inspire
    ############################################################
    if message.content.startswith('$inspire'):
        quote = get_quote()
        await message.channel.send(f'You seem to be in need of scouting motivation, {name}. Here is a quote.')
        await message.channel.send(quote)
    
    ############################################################
    #add encouragements to the 'grab bag' list, only if phrase is unique and not already in the list
    #use: 
    #   $add encouraging_phrase_here
    ############################################################
    if message.content.startswith("$add "):
        encouragement = load_encouragement_keywords()   #load list of encouragement phrases!
        flag=add_encouraging_message(message,encouragement)   #return flag; if true, then phrase is not in keywords!
        if flag:
            await message.channel.send(f"Added to the list, {name}!")
            save_encouragement_keywords(encouragement)   #will write to keyword_lists/encouragement.txt
        else:
            await message.channel.send(f"This phrase is already in the list, {name}!")
    
    ############################################################
    #Print the key to our shorthand for star spawning locations!
    #use: 
    #   $loc shorthand
    #e.g., '$loc nc' will output 'North Crandor'
    ############################################################
    if message.content.startswith("$loc "):
        
        loc_shorthand, loc_key = print_loc_key(message)
        await message.channel.send(f'{loc_shorthand} = {loc_key}')
        await message.channel.send(f'See https://locations.dust.wiki for exact location!')
    
    ############################################################
    #print wave guide URL into the chat!
    #use:
    #    $guide
    ############################################################
    if message.content.startswith("$guide"):
        await message.channel.send(print_guide())
       
    ############################################################
    #print current wave time into the chat!   
    #use:
    #    $wave
    ############################################################
    if message.content.startswith("$wave"):
        
        wave_message = create_wave_message()
        
        await message.channel.send(wave_message)
        
    ############################################################
    #Print the current poof time estimate for a world!
    #use: 
    #   $poof world
    #e.g., '$poof 308' will output '+30' if +30 is the poof time
    ############################################################
    if message.content.startswith("$poof "):
        
        world = message.content[6:].strip()
        poof_message = create_poof_message(world)
        
        await message.channel.send(poof_message)
    
    
    ############################################################
    #Print the current call time estimate for a star given its
    #world and tier!
    #use: 
    #   $hold world tier
    #e.g., '$hold 308 7' (for a t7 star in world 308)
    ############################################################
    if message.content.startswith("$hold "):
        
        #separate components of the message (default delimiter is ' ')
        components = message.content.split()
        world = components[1]
        tier = components[2]
        
        call_message = create_call_message(world,tier)
        
        await message.channel.send(call_message)
        
        

client.run(os.getenv('TOKEN'))