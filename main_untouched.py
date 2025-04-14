import discord
import os
from dotenv import load_dotenv
import random
from discord.ext import commands
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from commands import *   #separate from the discord.ext hoohaw. this is my .py file.
from pull_from_gs import *

#load environment variables from 'token.env' file
load_dotenv('token.env')

#define intents; required to read message content in on_message
intents = discord.Intents.default()
intents.message_content = True

#create bot instance (inherits from discord.Client)
bot = commands.Bot(command_prefix="$", intents=intents)

# Begin scheduler...need for $start_jokes command; will generate scheduled messages!
scheduler = AsyncIOScheduler()

#@bot.even is used to register an event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    scheduler.start()
    
@bot.event
#the function is called when something happens (in this case, when the bot receives message)
async def on_message(message):
    
    #if the message is from the bot, the bot will not respond...and this function will "exit"
    if message.author == bot.user:
        return
    
    #grab display name (name) and username of the message author
    name = message.author.display_name
    username = message.author.name

    ############################################################
    #If message includes any of the keywords, random greeting will print
    #use: 
    #   e.g., user types "hello"
    #   bot might respond with "uWu, {name}!"
    ############################################################
    greeting_keywords = pull_greeting_keywords()
    if any(word in message.content for word in greeting_keywords):
        common_greetings, wooly_dislike_list = greeting_response_keywords()
        if (name not in wooly_dislike_list) & (username not in wooly_dislike_list):
            chosen_greeting = random.choice(common_greetings)
        else:
            chosen_greeting = "Get out"
        await message.channel.send(f"{chosen_greeting}, {name}!")
        return

    
    ############################################################
    #If message includes any of the keywords, random encouraging message will print
    #use: 
    #   e.g., user types "I am feeling upset"
    #   bot might respond with "Smile, {name}."
    ############################################################
    sad_keywords = load_sad_keywords()
    if any(word in message.content for word in sad_keywords):
        encouragement = load_encouragement_keywords()
        chosen_encouragement = random.choice(encouragement)
        await message.channel.send(chosen_encouragement)
        return

    #pass to command processor if not matched above
    await bot.process_commands(message)

############################################################
#Print random inspirational quote
#use: 
#   $inspire
############################################################
@bot.command()
async def inspire(ctx):
    quote = get_zen_quote()
    #await ctx.send(f'You seem to be in need of scouting motivation, {ctx.author.display_name}. Here is a quote.')
    await ctx.send(quote)

############################################################
#Print random factoid quote
#use: 
#   $rand
############################################################
@bot.command()
async def rand(ctx):
    quote = get_random_quote()
    await ctx.send(quote)

############################################################
#print a random joke, written by our own tj44
#use: 
#   e.g., $haha
#   print randomly-generated joke
############################################################
@bot.command()
async def haha(ctx):
    joke_list = load_tj_jokes()
    chosen_joke = random.choice(joke_list)
    await ctx.send(chosen_joke)

############################################################
#add encouragements to the 'grab bag' list, only if phrase is unique and not already in the list
#use: 
#   $add encouraging_phrase_here
############################################################
@bot.command()
async def add(ctx, *, msg):   #fun little syntax note: the * means “capture the rest of the   
                                   #user’s message as one single string called msg”
                                   #So $add you are a wizard → msg = "you are a wizard"
    
    encouragement = load_encouragement_keywords()
    flag = add_encouraging_message(ctx.message, encouragement)
    if flag:
        await ctx.send(f"Added to the list, {ctx.author.display_name}!")
        save_encouragement_keywords(encouragement)
    else:
        await ctx.send(f"This phrase is already in the list, {ctx.author.display_name}!")

############################################################
#Print the key to our shorthand for star spawning locations!
#use: 
#   $loc shorthand
#e.g., '$loc nc' will output 'North Crandor'
############################################################
@bot.command()
async def loc(ctx, shorthand):
    loc_shorthand, loc_key = print_loc_key(ctx.message)
    await ctx.send(f'{loc_shorthand} = {loc_key}')
    await ctx.send('See https://locations.dust.wiki for exact location!')

############################################################
#print wave guide URL into the chat!
#use:
#    $guide
############################################################
@bot.command()
async def guide(ctx):
    await ctx.send(print_guide())

############################################################
#print current wave time into the chat!   
#use:
#    $wave
############################################################    
@bot.command()
async def wave(ctx):
    wave_message = create_wave_message()
    await ctx.send(wave_message)

############################################################
#Print the current poof time estimate for a world!
#use: 
#   $poof world
#e.g., '$poof 308' will output '+30' if +30 is the poof time
############################################################
@bot.command()
async def poof(ctx, world):
    poof_message = create_poof_message(world)
    await ctx.send(poof_message)

############################################################
#Print the current call time estimate for a star given its
#world and tier!
#use: 
#   $hold world tier
#e.g., '$hold 308 7' (for a t7 star in world 308)
############################################################
@bot.command()
async def hold(ctx, world, tier):
    call_message = create_call_message(world, tier)
    await ctx.send(call_message)
    
############################################################
#In a channel of your choosing, type command and the bot will randomly post
#a tj44 joke at the indicated time interval
#use: 
#   $start_jokes [hours]
#e.g., '$start_jokes 1' will print a joke every 1 hour in the channel
############################################################
@bot.command()

#registers this function as a bot command that is called when user types $start_jokes
async def start_jokes(ctx,hours=1):
    
    #create dictionary of all scheduled channel ids! otherwise, if I want 
    #to run $start_jokes in multiple channels, using the $start_jokes command
    #in one channel will overwrite the other channel's id
    #KEY = guild.id, value = channel.id
    scheduled_channel_ids = {}
    
    #stores the ID of the channel where the command was called
    scheduled_channel_id = ctx.channel.id
    await ctx.send(f"I will post tj44's haha-funnies here every {hours} hour(s)!")

    #defines the async function to send the joke message
    async def send_message():
        #grab channel
        channel = bot.get_channel(scheduled_channel_id)
        #if channel exists...send randomly chosen joke
        if channel:
            joke_list = load_tj_jokes()
            chosen_joke = random.choice(joke_list)
            await channel.send(chosen_joke)
    
    #scheduler functions must be non-async functions)
    #this function will schedule the async (send_message()) to run inside of the Discord bot's
    #event loop, even if APScheduler triggers it from a different thread
    def run_job():
        asyncio.run_coroutine_threadsafe(send_message(), bot.loop)

    #only add job if it hasn't been added yet
    #this *actually* schedules the event!
    if not scheduler.get_job("scheduled_msg"):
        #use scheduler that we defined at for on_ready()
        scheduler.add_job(
            run_job,
            trigger='interval',
            hours=hours,
            id="scheduled_msg"
        )    
        
############################################################
#In the same channel as above, type command and bot will cease typing
#a tj44 joke at the indicated time interval
#use: 
#   $stop_jokes
############################################################
@bot.command()
async def stop_jokes(ctx):
    #if $stop_jokes, then remove the job if said job exists.
    job = scheduler.get_job("scheduled_msg")
    if job:
        job.remove()
        await ctx.send("The posting of haha-funnies has been terminated.")
    else:
        await ctx.send("There's no active scheduled message.")

bot.run(os.getenv('TOKEN'))
