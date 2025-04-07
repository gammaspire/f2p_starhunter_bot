import discord
import os
from dotenv import load_dotenv
import random

from commands import get_quote
from commands import add_encouraging_message, load_encouragement_keywords, save_encouragement_keywords
from commands import print_loc_key

#load environment variables from 'token.env' file
load_dotenv('token.env')

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
    
    name = message.author.display_name
    
    #if the message is from the bot, the bot will not respond...and this function will "exit"
    if message.author == client.user:
        return
        
    #if the message includes any of the following, reply with a random greeting
    greeting_keywords = ['hello','Hello','hi','Hi','hey','Hey','hello bot','Hello bot','hi bot','Hi bot','hey bot',
                        'Hey bot']
    if any(word in message.content for word in greeting_keywords):
        
        common_greetings=['Eyyy','Heeeeey','Yo','Hello','Howdy','Hola','Greetings',
                      'Salutations','Hallo','Sup','Wassup','Haaaaay','Aloha','OMG','uWu',
                         'WAZZAAAAPPPP','Hewwo','NiHao','Guten Taggity','Yo yo','Bonjour',
                         'Ready to rumble']
        wooly_dislike_list=[]
        if name not in wooly_dislike_list:
            chosen_greeting=random.choice(common_greetings)
        else:
            chosen_greeting='Get out'
            
        await message.channel.send(f'{chosen_greeting}, {name}!')
    
    #if the message includes any of the following, reply with random encouragement
    sad_keywords = ['miserable','sad','unhappy','sadgams','angry','upset','depressed','infuriated','grumpy']
    if any(word in message.content for word in sad_keywords):
        encouragement = load_encouragement_keywords()   #load list of encouragement phrases!
        chosen_encouragement=random.choice(encouragement)
        await message.channel.send(f'{chosen_encouragement}, {name}.')
        
    if message.content.startswith('$inspire'):
        quote = get_quote()
        await message.channel.send(f'You seem to be in need of scouting motivation, {name}. Here is a quote.')
        await message.channel.send(quote)
    
    #add encouragements to the list
    if message.content.startswith("$add "):
        encouragement = load_encouragement_keywords()   #load list of encouragement phrases!
        flag=add_encouraging_message(message,encouragement)   #return flag; if true, then phrase is not in keywords!
        if flag:
            await message.channel.send(f"Added to the list, {name}!")
            save_encouragement_keywords(encouragement)   #will write to keyword_lists/encouragement.txt
        else:
            await message.channel.send(f"This phrase is already in the list, {name}!")
    
    #a key for our location shorthand
    if message.content.startswith("$loc "):
        
        loc_shorthand, loc_key = print_loc_key(message)
        await message.channel.send(f'{loc_shorthand} = {loc_key}')
        await message.channel.send(f'See https://locations.dust.wiki for exact location!')
    
    #DISSEMINATE THE GUIDE!
    if message.content.startswith("$guide"):
        await message.channel.send('Check out out Scouting Guide Here: https://docs.google.com/presentation/d/17bU-vGlOuT0MHBZ9HlTrfQEHKT4wHnBrLTV2_HC8LQU/')

client.run(os.getenv('TOKEN'))