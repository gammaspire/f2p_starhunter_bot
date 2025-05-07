import discord
import os
from dotenv import load_dotenv
import random
from discord.ext import commands
from discord.ui import View, Button
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from main_commands import *
from misc_commands import *
from pull_from_gsheet import *
from universal_functions import *

#load environment variables from 'token.env' file
load_dotenv('token.env')

#define intents; required to read message content in on_message
intents = discord.Intents.default()
intents.message_content = True

#create bot instance (inherits from discord.Client)
bot = commands.Bot(command_prefix="$", intents=intents, help_command=None)   #I am creating my own help_command

# Begin scheduler... will generate scheduled messages!
scheduler = AsyncIOScheduler()

#create dictionary of all scheduled channel ids! otherwise, if I want 
#to run $set_active in multiple channels, using the $set_active command
#in one channel will overwrite the other channel's id
#KEY = guild.id (server ID), value = channel.id
scheduled_channel_ids_active = {}   #this one specifically is for the active star jobs

#I am going to create a class for Discord button (which I will use to remove stars from the held_stars.json and add stars to the active_stars.json lists.
class CallStarButton(Button):
    def __init__(self, username, user_id, world, loc, tier):
        #super() inherits from discord.ui.Button class; calls the parent Button class's constructor
        #if I did not call super(), the button would exist without a label or style...and code may even break
        super().__init__(label='Call Star Now', style=discord.ButtonStyle.green)
        self.world=world
        self.loc=loc
        self.tier=tier
        self.username=username
        self.user_id=user_id
    
    #when I click the button, the star will be removed from the held_stars.json list
    async def callback(self, interaction: discord.Interaction):
        remove_held_star(self.world, 'held_stars.json')
        
        #if an entry with the same f2p world is not already in the .json file, add it!
        world_check = world_check_flag(self.world, 'active_stars.json')

        if world_check:
            await interaction.followup.send(f'A star for world {self.world} is already listed!')
            return
        
        add_star_to_list(self.username, self.user_id, self.world, self.loc, self.tier, 'active_stars.json')
        
        self.disabled = True
        
        self.style = discord.ButtonStyle.grey
        
        #edit message (that is, change the button and print the confirmation message.)
        await interaction.response.edit_message(view=self.view)
        await interaction.followup.send(f'Star moved to $active list!\nWorld: {self.world}\nLoc: {self.loc}\nTier: T{self.tier}')

#also create a class for the View, which will display the button in the Discord message
class CallStarView(View):
    def __init__(self, username, user_id, world, loc, tier, timeout=480):
        #super() here is inheriting from discord.ui.View, which is the class that handles buttons, 
        #dropdowns, and other UI elements in discord.
        super().__init__(timeout=timeout)
        self.add_item(CallStarButton(username, user_id, world, loc, tier))

        
#will use for sending backup and active star embeds   
async def send_embed(filename,destination,active=False,hold=False):
    #print active stars from .json
    #create embed!
    
    if active:
        title='Active Stars'
    else:
        title='Backup Stars'
    
    embed = discord.Embed(title=title,
                         color=0x1ABC9C)
    
    #populate the embed message with backup or active stars, if any
    embed_filled = embed_stars(filename, embed, active=active, hold=hold)
    await destination.send(embed=embed_filled)

    
################################################################################
################################################################################
################################################################################

#@bot.event is used to register an event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    scheduler.start()
    
    #refresh held_stars.json...don't want old backup stars infiltrating the scene
    with open('keyword_lists/held_stars.json', 'w') as f:
        json.dump([], f)
        
    #refresh active_stars.json...don't want old called stars infiltrating the scene, either    
    with open('keyword_lists/active_stars.json','w') as f:
        json.dump([],f)
    
    #ALSO, we must load the .json file which contains the scheduled active star jobs!
    active_jobs = load_json_file('keyword_lists/scheduled_active_jobs.json')
    
    for guild_id, job_info in active_jobs.items():
        guild_id = int(guild_id)
        channel_id, minutes = grab_job_ids(job_info)
        scheduled_channel_ids_active[guild_id] = channel_id
        
        #define the RUN JOB function, now coupled with our global send_active_list async function
        def run_job(gid=guild_id,channel_id=channel_id):
            #channel is same as ctx, and both are not the same as channel_id (I guess). I need ctx.
            channel = bot.get_channel(channel_id)
            asyncio.run_coroutine_threadsafe(send_embed('active_stars.json',
                                                    channel,active=True,hold=False), bot.loop)

        #define job id. if it is not in the scheduler, add and print success msg in terminal
        job_id = f"scheduled_msg_active_{guild_id}"
        if not scheduler.get_job(job_id):
            scheduler.add_job(run_job, trigger='interval', minutes=minutes, id=job_id)
            print(f"Restored scheduled active star messages for guild {guild_id} every {minutes} minutes.")

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


#a nice filter net to collect all unauthorized attempts to use certain restricted commands (e.g., $backups)
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        print(f'{ctx.author.name} ({ctx.author.display_name}) tried to use ${ctx.command}. Oops.')
        return
    
############################################################
#Print random inspirational quote
#use: 
#   $inspire
############################################################
@bot.command() #help='Prints a random inspirational quote, taken from https://zenquotes.io/api/random.\nExample usage: $inspire')
async def inspire(ctx):
    quote = get_zen_quote()
    #await ctx.send(f'You seem to be in need of scouting motivation, {ctx.author.display_name}. Here is a quote.')
    await ctx.send(quote)

############################################################
#Print random factoid quote
#use: 
#   $rand
############################################################
@bot.command() #help='Prints a random factoid, taken from https://uselessfacts.jsph.pl/.\nExample usage: $rand')
async def rand(ctx):
    quote = get_random_quote()
    await ctx.send(quote)

############################################################
#print a random joke, written by our own tj44
#use: 
#   e.g., $joke
#   print randomly-generated joke
############################################################
@bot.command() #help='Prints a random punny joke, courtesy of OSRS user tj44.\nExample usage: $joke')
async def joke(ctx):
    joke_list = load_tj_jokes()
    chosen_joke = random.choice(joke_list)
    await ctx.send(chosen_joke)

############################################################
#add encouragements to the 'grab bag' list, only if phrase is unique and not already in the list
#use: 
#   $add_inspo encouraging_phrase_here
############################################################
@bot.command() #help='Adds an "inspiring" message to the .json file.\nExample usage: $add_inspo you are a wizard')
async def add_inspo(ctx, *, msg):   #fun little syntax note: the * means “capture the rest of the   
                                    #user’s message as one single string called msg”
                                    #So $add_inspo you are a wizard → msg = "you are a wizard"
    
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
@bot.command(help='Prints the full location corresponding to our scouting loc shorthand.\nExample usage: $loc apa')
async def loc(ctx, shorthand):
    loc_shorthand, loc_key = print_loc_key(ctx.message)
    await ctx.send(f'{loc_shorthand} = {loc_key}')
    await ctx.send('See https://locations.dust.wiki for the full map of exact locations!')

############################################################
#print wave guide URL into the chat!
#use:
#    $guide
############################################################
@bot.command(help='Prints link to our scouting guide, courtesy of WoolyClamoth.\nExample usage: $guide')
async def guide(ctx):
    await ctx.send(print_guide())

############################################################
#print current wave time into the chat!   
#use:
#    $wave
############################################################    
@bot.command(help='Prints real-time message of current wave start time, end time, and the wave time at which the message was sent.\nExample usage: $wave')
async def wave(ctx):
    wave_start_time, wave_end_time, wave_time = get_wave_start_end()
    
    embed = discord.Embed(title='Current Wave Timer',
                         color=0x1ABC9C)
    
    embed.add_field(
        name=' ',
        value=(
            f"⭐ **Start:** <t:{wave_start_time}:t> (<t:{wave_start_time}:R>)\n"
            f"⭐ **End:** <t:{wave_end_time}:t> (<t:{wave_end_time}:R>)"
            "\n"
            "\n"
            f"⭐ **Wave Time When Message Was Sent:** +{wave_time}" 
        ),
        inline=False
    )
        
    await ctx.send(embed=embed)

############################################################
#Print the current poof time estimate for a world!
#use: 
#   $poof_time world
#e.g., '$poof_time 308' will output '+30' if +30 is the poof time
############################################################
@bot.command(help='Prints poof time for the entered world.\nExample usage: $poof_time 308')
async def poof_time(ctx, world):
    poof_message = create_poof_message(world)
    await ctx.send(poof_message)

############################################################
#Print the current call time estimate for a star given its
#world and tier!
#use: 
#   $eow world tier
#e.g., '$eow 308 7' (for a t7 star in world 308)
############################################################
@bot.command(help='Prints suggested EOW call time for the entered world. If no poof time is recorded for that world, then defaults to +85. Tiers 6-9 only.\nExample usage: $eow 308 9')
async def eow(ctx, world, tier):
    call_message = create_call_message(world, tier)
    await ctx.send(call_message)

############################################################
#hold star in held_stars.json file until time to release
#use: 
#   $hold world loc tier
#e.g., 
#   $hold 308 nc 8
############################################################
@bot.command(help='Records given world, loc, and tier into the $backups list.\nExample usage: $hold 308 akm 8')
async def hold(ctx, world=None, loc=None, tier=None):
    username = ctx.author.name
    user_id = ctx.author.id
    
    #load our location shorthand dictionary
    loc_dict = load_loc_dict()
    
    #remove 't' or 'T' from the tier string, if any
    tier = remove_frontal_corTex(tier)

    try:
        
        #if world_check returns TRUE, then the star is already in the JSON file!        
        world_check_held = world_check_flag(world,filename='held_stars.json')
                
        #if there is already a star registered in the .json file in 'world', cancel the request
        if world_check_held:
            await ctx.send(f'There is already a star being held for world {world}.\nCheck the list of backup stars with the $backups command.')
            return
        
        world_check_active = world_check_flag(world, 'active_stars.json')
        #if there is already a star registered in the .json file in 'world', cancel the request
        if world_check_active:
            await ctx.send(f'There is already an active star for world {world}.\nCheck the list of active stars with the $active command.')
            return
        
        #now compare wave time and eow suggested call time for star
        #if call_flag = True, can call the star now; if call_flag = False, add star to file and hold
        call_flag = check_wave_call(world,tier)   #will not run if call syntax is incorrect
        if call_flag:
            #view is what enables the button
            await ctx.send(f"<⭐ {ctx.author.mention}> CALL STAR: World {world}, {loc}, Tier {tier}",
                           view=CallStarView(username, user_id, world, loc, tier))  #CallStarView is a class
            return
                    
    #KeyError --> world is not in list of f2p worlds
    #TypeError --> user omitted world, loc, and/or tier from command
    except (KeyError, TypeError):
        await ctx.send(print_error_message())
        return
    
    #if not call flag, the command was typed correctly, AND there is not already an entry with the
    #world included in the command, add the held star to list and HOLD
    add_star_to_list(username, user_id, world, loc, tier, filename='held_stars.json')  
    await ctx.send(f"Holding the following ⭐:\nWorld: {world}\nLoc: {loc}\nTier: {tier}")
    
    #schedule the checking job; if star is ready to call, remove job!
    async def monitor_star():
        #re-check the call eligibility
        call_flag = check_wave_call(world,tier)

        if call_flag:
            
            #IF STAR IS IN ACTIVE (OR SM) AND REMOVED FROM BACKUPS BEFORE MANUALLY CALLED, REMOVE JOB.
            #maybe print a message in Discord that star is already active? or ignore entirely. not sure.
            
            #view is what enables the button; will remove held star from .json when clicked and add to $active
            await ctx.send(f"<⭐ {ctx.author.mention}> CALL STAR: World {world}, {loc}, Tier {tier}",
                           view=CallStarView(username, user_id, world, loc, tier))   #CallStarView is a class
            #redefine the unique job_id
            job_id = f"hold_{world}_{loc}_{tier}"
            #cancel the job
            scheduler.remove_job(job_id)
    
    #non-async wrapper for the scheduler
    def run_job():
        asyncio.run_coroutine_threadsafe(monitor_star(), bot.loop)

    #unique job ID (based on user + star details)
    job_id = f"hold_{world}_{loc}_{tier}"
    
    #will run run_job every one minute!
    if not scheduler.get_job(job_id):
        scheduler.add_job(run_job, 'interval', minutes=2, id=job_id)
    

############################################################
#print list of current backup stars in an aesthetic textbox
#use: 
#   $backups
############################################################    
@bot.command(help='Prints list of backup worlds. Restricted to @Ranked role.\nExample usage: $backups')
@commands.has_role('Ranked')
async def backups(ctx):    
    await send_embed('held_stars.json', ctx, hold=True)
    
    
############################################################
#manually remove backup star from the list
#(doing so will also remove the scheduled 'ping' to call)
#use: 
#   $remove f2p_world
#e.g., 
#   $remove 308
############################################################        
@bot.command(help='Manually removes star from $backups list. Restricted to @Ranked role.\nExample usage: $remove 308')
@commands.has_role('Ranked')
async def remove(ctx, world=None):
    
    #remove star from .json
    loc, tier = remove_held_star(world, 'held_stars.json', output_data=True)
    
    #cancel the job once done
    job_id = f"hold_{world}_{loc}_{tier}"
    scheduler.remove_job(job_id)
    
    await ctx.send(f"⭐ Removing the following star from backups list:\nWorld: {world}\nLoc: {loc}\nTier: {tier}")
    
    
############################################################
#print list of current active stars in an aesthetic textbox
#use: 
#   $active
############################################################     
@bot.command(help='Prints list of active stars.\nExample usage: $active')
async def active(ctx):
    await send_embed('active_stars.json', ctx, active=True)


############################################################
#add active star to the .json list
#use: 
#   $call world loc tier
#e.g., 
#   $call 308 akm 8
############################################################  
@bot.command(help='Calls star and moves to $active list. Restricted to @Ranked role.\nExample usage: $call 308 akm 8')
@commands.has_role('Ranked')
async def call(ctx, world, loc, tier):
    
    #load list of f2p worlds
    f2p_world_list = load_f2p_worlds()
    
    tier = remove_frontal_corTex(tier)
    
    #if an entry with the same f2p world is not already in the .json file, add it!
    world_check = world_check_flag(world, 'active_stars.json')
    
    if world_check:
        await ctx.send(f'A star for world {world} is already listed!')
        return
    
    if (str(world) not in f2p_world_list) | (int(tier)>9) | (int(tier)<1):
        await ctx.send(print_error_message())
        return
    
    #assumes star finder is the individual who submitted the message...ah well.
    username = ctx.author.name
    user_id = ctx.author.id
    
    #add star to .json
    add_star_to_list(username, user_id, world, loc, tier, 'active_stars.json')

    await ctx.send(f"⭐ Star moved to $active list!\nWorld: {world}\nLoc: {loc}\nTier: {tier}")
        
    
############################################################
#In a channel of your choosing, type command and the bot will post
#list of active stars every x minutes
#use: 
#   $start_active_loop [minutes]
#e.g., '$start_active_loop 30' will print the list every 30 minutes in the channel
############################################################
@bot.command(help='Sets up the bot to send $active list in the designated channel every x minutes. Restricted to @Mods role.\nExample usage: $start_active_loop')
@commands.has_role('Mods')

#registers this function as a bot command that is called when user types $start_active_loop
async def start_active_loop(ctx,minutes=60):
    
    #unique identifier for a Discord SERVER
    guild_id = ctx.guild.id
    
    #associates server ID with the channel ID
    scheduled_channel_ids_active[guild_id] = ctx.channel.id
    
    #stores the ID of the channel where the command was called
    scheduled_channel_id = ctx.channel.id
    await ctx.send(f"Active stars will be posted in this channel every {minutes} minute(s)!")
    
    #scheduler functions must be non-async functions)
    #this function will schedule the async (send_message()) to run inside of the Discord bot's
    #event loop, even if APScheduler triggers it from a different thread
    def run_job():
        embed_list = asyncio.run_coroutine_threadsafe(send_embed('active_stars.json',
                                                    ctx,active=True,hold=False), bot.loop)
    
    #creates job id given the server! this way, I can have multiple jobs for multiple servers :-)
    job_id = f"scheduled_msg_active_{guild_id}"    

    #only add job if it hasn't been added yet
    #this *actually* schedules the event!
    if not scheduler.get_job(job_id):
        #use scheduler that we defined at for on_ready()
        scheduler.add_job(run_job, trigger='interval', minutes=minutes, id=job_id)    

    #save to JSON so it persists (i.e., not wiped from memory when main.py is terminated)
    all_jobs = load_json_file('keyword_lists/scheduled_active_jobs.json')   #if .json already exists, load
    all_jobs[str(guild_id)] = {
        'channel_id': scheduled_channel_ids_active[guild_id],
        'interval': minutes
    }
    save_json_file(all_jobs, 'keyword_lists/scheduled_active_jobs.json')

############################################################
#In the same channel as above, type command and bot will cease typing
#the list of active stars at the indicated time interval
#use: 
#   $stop_active_loop
############################################################
@bot.command(help="Terminates the bot's sending of $active list in the designated channel every x minutes, if applicable. Restricted to @Mods role.\nExample usage: $stop_active_loop")
@commands.has_role('Mods')
async def stop_active_loop(ctx):
    
    #get server ID
    guild_id = ctx.guild.id
    
    #pull the job id (again, given the server id)
    job_id = f"scheduled_msg_active_{ctx.guild.id}"
    
    #if $stop_active_loop, then remove the job if said job exists.
    job = scheduler.get_job(job_id)
    if job:
        job.remove()
        await ctx.send("The posting of active stars in this channel has been terminated.")
    else:
        await ctx.send("There's no active scheduled message.")
    
    #remove job from the the dictionary! that is...clear from memory.
    #if guild_id not found, the "None" ensures there is no output error message in terminal
    scheduled_channel_ids_active.pop(guild_id, None)
    #load all jobs .json file
    all_jobs = load_json_file('keyword_lists/scheduled_active_jobs.json')
    #remove the job associated with the server!
    all_jobs.pop(str(guild_id), None)
    #re-write .json file
    save_json_file(all_jobs, 'keyword_lists/scheduled_active_jobs.json')
    

############################################################
#Creating a $help command that is a little cleaner than the default
#use: 
#   $help
############################################################   
@bot.command(help='Prints this list of abridged help information.\nExample usage: $help')
async def help(ctx):
    embed = discord.Embed(title='F2P Starhunter Help Menu',description='Commands List:',color=0x1ABC9C)
    for command in bot.commands:
        if command.help!=None:
            embed.add_field(name=f'${command.name}',value=command.help,inline=False)
    await ctx.send(embed=embed)
 
    
    
bot.run(os.getenv('TOKEN'))