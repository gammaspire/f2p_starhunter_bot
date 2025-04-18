import discord
import os
from dotenv import load_dotenv
import random
from discord.ext import commands
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from main_commands import *
from misc_commands import *
from pull_from_gsheet import *

#load environment variables from 'token.env' file
load_dotenv('token.env')

#define intents; required to read message content in on_message
intents = discord.Intents.default()
intents.message_content = True

#create bot instance (inherits from discord.Client)
bot = commands.Bot(command_prefix="$", intents=intents)

# Begin scheduler...need for $start_jokes command; will generate scheduled messages!
scheduler = AsyncIOScheduler()

#create dictionary of all scheduled channel ids! otherwise, if I want 
#to run $start_jokes in multiple channels, using the $start_jokes command
#in one channel will overwrite the other channel's id
#KEY = guild.id (server ID), value = channel.id
scheduled_channel_ids_jokes = {}   #this one specifically is for the JOKES


#@bot.even is used to register an event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    scheduler.start()
    
    #refresh held_stars.json...don't want old backup stars infiltrating the scene
    with open('keyword_lists/held_stars.json', 'w') as f:
        json.dump([], f)
    
    #ALSO, we must load the .json file which contains the scheduled joke jobs!
    joke_jobs = load_json_file('keyword_lists/scheduled_joke_jobs.json')
    for guild_id, job_info in joke_jobs.items():
        guild_id = int(guild_id)
        channel_id, minutes = grab_job_ids(job_info)
        scheduled_channel_ids_jokes[guild_id] = channel_id
        
        #define the RUN JOB function, now coupled with our global send_joke async function
        def run_job(gid=guild_id,channel_id=channel_id):
            asyncio.run_coroutine_threadsafe(send_joke(bot, channel_id), bot.loop)
        
        #define job id. if it is not in the scheduler, add and print success msg in terminal
        job_id = f"scheduled_msg_{guild_id}"
        if not scheduler.get_job(job_id):
            scheduler.add_job(run_job, trigger='interval', minutes=minutes, id=job_id)
            print(f"Restored scheduled jokes for guild {guild_id} every {minutes} minutes.")
    
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
    #   bot might respond with "Howdy, {name}!"
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
#   $eow world tier
#e.g., '$eow 308 7' (for a t7 star in world 308)
############################################################
@bot.command()
async def eow(ctx, world, tier):
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
async def start_jokes(ctx,minutes=60):
    
    #unique identifier for a Discord SERVER
    guild_id = ctx.guild.id
    
    #associates server ID with the channel ID
    scheduled_channel_ids_jokes[guild_id] = ctx.channel.id
    
    #stores the ID of the channel where the command was called
    scheduled_channel_id = ctx.channel.id
    await ctx.send(f"I will post tj44's haha-funnies here every {minutes} minute(s)!")

    #scheduler functions must be non-async functions)
    #this function will schedule the async (send_message()) to run inside of the Discord bot's
    #event loop, even if APScheduler triggers it from a different thread
    def run_job():
        asyncio.run_coroutine_threadsafe(send_joke(bot, scheduled_channel_id), bot.loop)

    #creates job id given the server! this way, I can have multiple jobs for multiple servers :-)
    job_id = f"scheduled_msg_{guild_id}"    
        
    #only add job if it hasn't been added yet
    #this *actually* schedules the event!
    if not scheduler.get_job(job_id):
        #use scheduler that we defined at for on_ready()
        scheduler.add_job(run_job, trigger='interval', minutes=minutes, id=job_id)    
    
    #save to JSON so it persists (i.e., not wiped from memory when main.py is terminated)
    all_jobs = load_json_file('keyword_lists/scheduled_joke_jobs.json')   #if .json already exists, load
    all_jobs[str(guild_id)] = {
        'channel_id': scheduled_channel_ids_jokes[guild_id],
        'interval': minutes
    }
    save_json_file(all_jobs, 'keyword_lists/scheduled_joke_jobs.json')
    
############################################################
#In the same channel as above, type command and bot will cease typing
#a tj44 joke at the indicated time interval
#use: 
#   $stop_jokes
############################################################
@bot.command()
async def stop_jokes(ctx):
    
    #get server ID
    guild_id = ctx.guild.id
    
    #pull the job id (again, given the server id)
    job_id = f"scheduled_msg_{ctx.guild.id}"
    
    #if $stop_jokes, then remove the job if said job exists.
    job = scheduler.get_job(job_id)
    if job:
        job.remove()
        await ctx.send("The posting of haha-funnies has been terminated.")
    else:
        await ctx.send("There's no active scheduled message.")
    
    #remove job from the the dictionary! that is...clear from memory.
    #if guild_id not found, the "None" ensures there is no output error message in terminal
    scheduled_channel_ids_jokes.pop(guild_id, None)
    #load all jobs .json file
    all_jobs = load_json_file('keyword_lists/scheduled_joke_jobs.json')
    #remove the job associated with the server!
    all_jobs.pop(str(guild_id), None)
    #re-write .json file
    save_json_file(all_jobs, 'keyword_lists/scheduled_joke_jobs.json')

############################################################
#hold star in held_stars.json file until time to release
#use: 
#   $hold world loc tier
#e.g., 
#   $hold 308 nc 8
############################################################
@bot.command()
async def hold(ctx, world=None, loc=None, tier=None):
    username = ctx.author.name
    user_id = ctx.author.id
    
    #load our location shorthand dictionary
    loc_dict = load_loc_dict()
    
    
    #remove 't' or 'T' from the tier string, if any
    tier = remove_frontal_corTex(tier)

    try:
        
        #if world_check returns TRUE, then the star is already in the JSON file!        
        world_check = world_check_flag(world,filename='held_stars.json')
                
        #if there is already a star registered in the .json file in 'world', cancel the request
        if world_check:
            await ctx.send(f'There is already a star being held for world {world}.\nCheck the list of backup stars with the $backups command.')
            return
        
        #now compare wave time and eow suggested call time for star
        #if call_flag = True, can call the star now; if call_flag = False, add star to file and hold
        call_flag = check_wave_call(world,tier)   #will not run if call syntax is incorrect
        if call_flag:
            
            await ctx.send(f"<⭐ {ctx.author.mention}> CALL STAR: World {world}, {loc}, Tier {tier}")
            
            return
                           
    except (KeyError, TypeError):
        await ctx.send('Missing or invalid arguments!\nSyntax: $hold f2p_world loc_shorthand tier_6789\nExample: $hold 308 akm 8')
        remove_held_star(world, 'held_stars.json')
        return
    
    #if not call flag, the command was typed correctly, AND there is not already an entry with the
    #world included in the command, add the held star to list and HOLD
    add_held_star(username, user_id, world, loc, tier)  
    await ctx.send(f"⭐ Holding the following star:\nWorld: {world}\nLoc: {loc}\nTier: T{tier}")
    
    #schedule the checking job
    async def monitor_star():
        #re-check the call eligibility
        call_flag = check_wave_call(world,tier)

        if call_flag:
            await ctx.send(f"<⭐ {ctx.author.mention}> CALL STAR: World {world}, {loc}, Tier {tier}")
            #remove star from .json
            remove_held_star(world, 'held_stars.json')
            #redefine the unique job_id
            job_id = f"hold_{ctx.guild.id}_{world}_{loc}_{tier}"
            #cancel the job once done
            scheduler.remove_job(job_id)

            
            
    #non-async wrapper for the scheduler
    def run_job():
        asyncio.run_coroutine_threadsafe(monitor_star(), bot.loop)

    #unique job ID (based on user + star details)
    job_id = f"hold_{ctx.guild.id}_{world}_{loc}_{tier}"
    
    if not scheduler.get_job(job_id):
        scheduler.add_job(run_job, 'interval', minutes=1, id=job_id)

    #experiment with highlights and attractive hexcolors
    

############################################################
#print list of current backup stars in an aesthetic textbox
#use: 
#   $backups
############################################################    
@bot.command()
async def backups(ctx):
        
    #create embed!
    embed = discord.Embed(title='Backup Stars',
                          description='List of held stars for current wave!',
                         color=0x1ABC9C)
    
    #populate the embed message with backup stars, if any
    embed_filled = embed_backups('held_stars.json', embed)
    
    await ctx.send(embed=embed_filled)
    
    
############################################################
#manually remove backup star from the list
#(doing so will also remove the scheduled 'ping' to call
#use: 
#   $remove f2p_world
#e.g., 
#   $remove 308
############################################################        
@bot.command()
async def remove(ctx, world=None):
    
    #remove star from .json
    loc, tier = remove_held_star(world, 'held_stars.json', output_data=True)
    
    #cancel the job once done
    job_id = f"hold_{ctx.guild.id}_{world}_{loc}_{tier}"
    scheduler.remove_job(job_id)
    
    await ctx.send(f"⭐ Removing the following star from backups list:\nWorld: {world}\nLoc: {loc}\nTier: T{tier}")


############################################################
#print list of current active stars in an aesthetic textbox
#use: 
#   $active
############################################################     
    
    
    
    
bot.run(os.getenv('TOKEN'))