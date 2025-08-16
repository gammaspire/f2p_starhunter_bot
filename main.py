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


################################################################################
################################################################################
################################################################################


#load environment variables from 'token.env' file
load_dotenv('token.env')

#define intents; required to read message content in on_message
intents = discord.Intents.default()
intents.members = True   #need to detect when new members join :-)
intents.message_content = True

#create bot instance (inherits from discord.Client)
bot = commands.Bot(command_prefix="$", intents=intents, help_command=None)   #I am creating my own help_command

################################################################################
################################################################################
################################################################################

#JOB SCHEDULING STUFF

#begin scheduler... will generate scheduled messages!
scheduler = AsyncIOScheduler()

#create dictionary of all scheduled channel ids! otherwise, if I want 
#to run $set_active in multiple channels, using the $set_active command
#in one channel will overwrite the other channel's id
#KEY = guild.id (server ID), value = channel.id
scheduled_channel_ids_active = {}   #this one specifically is for the active star jobs
scheduled_channel_ids_hoplist = {}  #and this one specifically is for the hoplist jobs


#---FUNCTIONS FOR THE RE-ACTIVATION OF SCHEDULED JOBS UPON BOT RESTART---
def run_active(bot, guild_id, channel_id, message_id):
    channel = bot.get_channel(channel_id)
    asyncio.run_coroutine_threadsafe(send_embed("keyword_lists/active_stars.json", channel, active=True, 
                                                hold=False, message_id=message_id), bot.loop)

def run_hoplist(bot, guild_id, channel_id, message_id):
    channel = bot.get_channel(channel_id)
    asyncio.run_coroutine_threadsafe(send_hoplist_message(channel, message_id), bot.loop)

################################################################################
################################################################################
################################################################################

#EMBED CLASS STUFF

#custom Discord button class that will allow users to move a star from 'held_stars.json' to 'active_stars.json'
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
        remove_star(self.world, 'held_stars.json')
        
        #if an entry with the same f2p world is not already in the .json file, add it!
        world_check = world_check_flag(self.world, filename='active_stars.json')

        if world_check:
            await interaction.followup.send(f'A star for world {self.world} is already listed!')
            return
        
        add_star_to_list(self.username, self.user_id, self.world, self.loc, self.tier, 'active_stars.json')
        
        self.disabled = True
        
        self.style = discord.ButtonStyle.grey
        
        #edit message (that is, change the button and print the confirmation message.)
        await interaction.response.edit_message(view=self.view)
        await interaction.followup.send(f'Star moved to $active list!\nWorld: {self.world}\nLoc: {self.loc}\nTier: T{self.tier}')


#-----------------------------
#custom View class that holds the button
#-----------------------------
class CallStarView(View):
    def __init__(self, username, user_id, world, loc, tier, timeout=600):
        #super() here is inheriting from discord.ui.View, which is the class that handles buttons, 
        #dropdowns, and other UI elements in discord.
        super().__init__(timeout=timeout)
        self.add_item(CallStarButton(username, user_id, world, loc, tier))

        
################################################################################
################################################################################
################################################################################        
        
#ASYNC STUFF FOR GENERATING STAR EMBEDS AND HOPLIST MESSAGES
    
#will use for sending backup and active star embeds   
#message_id only relevant for $start_active_loop. it will tell the function which embed message to modify like a bulletin board!
async def send_embed(filename,destination,active=False,hold=False,message_id=None):
    
    if active:
        title='Active Stars'
    else:
        title='Backup Stars'
    
    #define empty embed
    embed = discord.Embed(title=title,
                         color=0x1ABC9C)
    
    #populate the embed message with backup or active stars, if any
    embed_filled = embed_stars(filename, embed, active=active, hold=hold)
    
    #if there is a message_id, then refresh the "bulletin board" attached to $start_active_loop
    if message_id:
        try:
            message = await destination.fetch_message(message_id)
            await message.edit(embed=embed_filled)
            return message.id
        
        except discord.NotFound:
            #if the message doesn't exist anymore, fallback to sending a new one
            message = await destination.send(embed=embed_filled)
            return message.id
    else:
        message = await destination.send(embed=embed_filled)
        #don't use return message.id here -- need message_id to be None for $active and $backups commands


#will use to generate (or update) the $start_hop_list message
async def send_hoplist_message(channel, message_id):
    """Fetches and edits the hoplist loop message; sends a new one if missing."""
    text = generate_hoplist_text()
    if channel is None:
        print("Channel not found, skipping hoplist update.")
        return
    try:
        msg = await channel.fetch_message(message_id)   #grab message id...
        await msg.edit(content=text)                    #edit message content...
    except discord.NotFound:
        await channel.send(text)
        
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
    
    # --- Restore ACTIVE jobs ---
    active_jobs = load_json_file('keyword_lists/scheduled_active_jobs.json')   #load active jobs .json file
    #for every active job in the file, if any -- define guild id, grab channel_id (where message is), the number of minutes
    #between each message refresh, and the id of the message to be refreshed
    #then, add the active job to the local active guild-channel dictionary
    for guild_id, job_info in active_jobs.items():
        guild_id = int(guild_id)
        channel_id, minutes = grab_job_ids(job_info)
        message_id = job_info.get("message_id")

        scheduled_channel_ids_active[guild_id] = channel_id

        #re-define the job id
        job_id = f"scheduled_msg_active_{guild_id}"
        #if the job is not yet active...activate it.
        if not scheduler.get_job(job_id):
            scheduler.add_job(run_active, trigger='interval', minutes=minutes, id=job_id,
                args=[bot, guild_id, channel_id, message_id]  #pass arguments here for run_active!
            )
            #confirmation message.
            print(f"Restored scheduled active star messages for guild {guild_id} every {minutes} minutes.")

    # --- Restore HOPLIST jobs ---
    hoplist_jobs = load_json_file('keyword_lists/scheduled_hoplist_jobs.json')
    for guild_id, job_info in hoplist_jobs.items():
        guild_id = int(guild_id)
        channel_id = job_info["channel_id"]
        minutes = job_info["interval"]
        message_id = job_info.get("message_id")

        scheduled_channel_ids_hoplist[guild_id] = channel_id

        job_id = f"scheduled_msg_hoplist_{guild_id}"
        if not scheduler.get_job(job_id):
            scheduler.add_job(run_hoplist, trigger='interval', minutes=minutes, id=job_id,
                args=[bot, guild_id, channel_id, message_id]  #arguments for run_hoplist!
            )
            print(f"Restored scheduled hoplist messages for guild {guild_id} every {minutes} minutes.")

            
################################################################################
################################################################################
################################################################################ 


#@bot.event is used to register an event
#create a welcome message that is DM'd to the user!
@bot.event
async def on_member_join(member):
    
    #I only want new members joining F2P StarHunt to trigger this welcome message!
    starhunt_server_id = int(os.getenv("STARHUNT_GUILD_ID"))
    
    if member.guild.id != starhunt_server_id:
        return  #ignoreeeeeeee members joining other servers
    
    channel = None #initialize the variable, in case the first "except" is not triggered
    
    #create the embed message (nice formatting, 10/10)
    embed_message = prep_welcome_message(member)
    
    try:
        await member.send(embed=embed_message)
        print(f'Successfully sent DM welcome message to {member.name}!')
    
    #if user has discord DM privacy settings enabled, just send the message into the channel
    except discord.Forbidden:
        
        print(f"Could not send DM to {member.name}. Trying #general channel...")  
        
        channel_id = int(os.getenv("WELCOME_CHANNEL_ID"))
        channel = member.guild.get_channel(channel_id)
        await channel.send(embed=embed_message)
        
        print('Success!')

    except Exception as e:
        print(f"Non-Forbidden error sending DM welcome message to {member.name}: {e}")
        print("Trying #general channel...")
        
        if channel:
            await channel.send(embed=embed_message)
            print('Success!')
            return
        
        print('Error sending message, well, anywhere.')
            
            
            
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
    #   bot might respond with "Absorb some sunshine."
    ############################################################
    sad_keywords = set(load_sad_keywords())
    
    if any(word in message.content for word in sad_keywords):
        encouragement = load_encouragement_keywords()
        chosen_encouragement = random.choice(encouragement)
        
        #there is a secret response prompt -- "sarcasm"
        #in this case, find the (or a) sad word in the user's message and *sArCaStiFy iT*
        if chosen_encouragement=='sarcasm':
            
            #quickest approach computationally to finding the sad word is to convert both lists to a set, 
            #then find the sad word that triggered this function
            encouragement=set(encouragement)
            
            try:
                word = list(encouragement.intersection(sad_keywords))[0]
            except:
                word = 'unhappy'
            
            chosen_encouragement = sarcastify_word(word)
        
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


################################################################################
################################################################################
################################################################################

    
############################################################
#Print random inspirational quote
#use: 
#   $inspire
############################################################
@bot.command() #help='Prints a random inspirational quote, taken from Dave Tarnowski's "Disappointing Affirmations.\nExample usage: $inspire')
async def inspire(ctx):
    affirmations = load_affirmations()
    await ctx.send(random.choice(affirmations))

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

################################################
#ask the magic conch shell to resolve your indecision.
#use: 
#   $conch [your question]
################################################        
@bot.command()
async def conch(ctx):

    await ctx.send("Type your yes/no question below.")
    
    #if user invoking the conch is tysen, react with poo emoji
    if ctx.author.name=='deleted_user102727':
        await ctx.message.add_reaction("💩")

    def check(user_message):
        return (user_message.author == ctx.author) & (user_message.channel == ctx.channel)

    try:
        #bot waits for message sent by same author AND in same channel
        question = await bot.wait_for("message", timeout=20.0, check=check)
        
        #the bot checks that the question ENDS in a question mark. if not, no response.
        if not question.content.endswith("?"):
            await ctx.send("Your grammar is abysmal. Wake me when you decide to use question marks.")
            return
        
        #select and send response!
        response = random.choice(load_conch_responses())
        await ctx.send(f"🌀 {response} 🌀")
    
    #if user doesn't respond within 20 seconds, the bot.wait_for will return an error and this message will be sent...
    except asyncio.TimeoutError:
        await ctx.send("🌀 You took too long typing your query. The conch has gone back to sleep. 🌀")

################################################
#disagree? VOCALIZE YOUR DISAPPROVAL HERE!
#use: 
#   $strike
################################################ 
@bot.command()
async def strike(ctx):
    
    protests = load_protests()
    chosen_protest = random.choice(protests)
    await ctx.send(chosen_protest)

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
    
    await ctx.message.add_reaction("👋")
    await ctx.send(embed=embed)

############################################################
#Print the current poof time estimate for a world!
#use: 
#   $poof_time world
#e.g., '$poof_time 308' will output '+30' if +30 is the poof time
############################################################
@bot.command(help='Prints poof time for the entered world.\nExample usage: $poof_time 308')
async def poof_time(ctx, world):
    
    #load list of f2p worlds
    f2p_world_list = load_f2p_worlds()

    if world not in f2p_world_list:
        await ctx.send('Are you kidding? USE A VALID F2P WORLD.')
        return
    
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
    call_message = create_eow_message(world, tier)
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

    #check if user remembered to include world, loc, and tier arguments
    if not world or not loc or not tier:
        await ctx.send(print_error_message(command='hold'))
        await ctx.send('-# Come on, now. You should know better.')
        return

    #now check if the world is f2p; if not, goodbye.
    if str(world) not in load_f2p_worlds():
        await ctx.send(print_error_message(command='hold')+'\n'+'-# Use your noggin next time.')
        return

    tier = remove_frontal_corTex(tier)
    
    #parse the tier...which must be between 6 and 9
    try:
        if not (6 <= int(tier) <= 9):
            await ctx.send('Please make sure you are holding a star with a tier of at least 6.')
            await ctx.send(f'-# You really wanted to hold a t{tier} star? Good heavens.')
            return
    except:
        await ctx.send(print_error_message(command='hold'))
        return
    
    #check if the world is already held or called
    #if so, cancel the request
    if world_check_flag(world, filename='held_stars.json'):
        await ctx.send(f'There is already a held star for world {world}.')
        return
    if world_check_flag(world, filename='active_stars.json'):
        await ctx.send(f'There is already an active star for world {world}.')
        return

    #load our location shorthand dictionary
    loc_dict = load_loc_dict()

    #if it is indeed time to call the star, CALL THE STAR
    #compares wave time and eow suggested call time for star
    #if check_wave_call = True, can call the star now; if call_flag = False, add star to file and hold
    if check_wave_call(world, tier):
        await ctx.send(f"<⭐ {ctx.author.mention}> CALL STAR: World {world}, {loc}, Tier {tier}",
                       view=CallStarView(username, user_id, world, loc, tier))   #CallStarView is a class
        return

    #lastly...if none of the above catches terminated the function, hold the star~
    #...and then proceed to the scheduler functions below
    try:
        add_star_to_list(username, user_id, world, loc, tier, filename='held_stars.json')
        await ctx.send(f"Holding the following ⭐:\nWorld: {world}\nLoc: {loc}\nTier: {tier}")
    except Exception as e:
        await ctx.send(f"Failed to hold star due to the following error: {e}")

    #schedule the checking job; if star is ready to call, remove job!
    async def monitor_star():

        #if the world is in the $active list, REMOVE THE SCHEDULED JOB.
        if world_check_flag(world,filename='active_stars.json'):
            #redefine the unique job_id
            job_id = f"hold_{world}_{tier}"
            #cancel the job
            scheduler.remove_job(job_id)
            await ctx.send(f"⭐ HELD STAR World {world} {loc} t{tier} is now in the $active list and has automatically been removed from $backups.")

        #if world is not in $active list, re-check the call eligibility
        call_flag = check_wave_call(world,tier)

        if call_flag:

            #view is what enables the button; will remove held star from .json when clicked and add to $active
            try:
                await ctx.send(f"<⭐ {ctx.author.mention}> CALL STAR: World {world}, {loc}, Tier {tier}",
                               view=CallStarView(username, user_id, world, loc, tier))   #CallStarView is a class
            except Exception as e:
                print(e)

            #redefine the unique job_id
            job_id = f"hold_{world}_{tier}"
            #cancel the job
            scheduler.remove_job(job_id)

    #non-async wrapper for the scheduler
    def run_job():
        asyncio.run_coroutine_threadsafe(monitor_star(), bot.loop)

    #THE FUNCTIONS DEFINED ABOVE WILL RUN WITH THE LAST FEW LINES
    #unique job ID (based on user + star details)
    job_id = f"hold_{world}_{tier}"

    #will run run_job every two minutes!
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
#   $remove_held f2p_world
#e.g., 
#   $remove_held 308
############################################################        
@bot.command(help='Manually removes star from $backups list. Restricted to @Ranked role.\nExample usage: $remove_held 308')
@commands.has_role('Ranked')
async def remove_held(ctx, world=None):
    
    if (world==None) | (world not in load_f2p_worlds()):
        await ctx.send('Did you forget to use a valid F2P world? I suspected as much. Try again.')
    
    #remove star from .json
    output = remove_star(world, 'held_stars.json', output_data=True)
    
    if output == (None, None):
        await ctx.send(f"World {world} not found in backups list.")
        return
    
    loc, tier = output
    job_id = f"hold_{world}_{tier}"

    #cancel job, if it exists
    try:
        scheduler.remove_job(job_id)
    except Exception as e:
        print(f"[Warning] Could not remove job '{job_id}': {e}")
    
    await ctx.send(f"⭐ Removing the following star from backups list:\nWorld: {world}\nLoc: {loc}\nTier: {tier}")


############################################################
#manually remove active star from the list
#use: 
#   $poof f2p_world
#e.g., 
#   $poof 308
############################################################        
@bot.command(help='Manually removes star from $active list (HOWEVER -- if star is still active on SM, it will not be removed). Restricted to @Ranked role.\nExample usage: $poof 308')
@commands.has_role('Ranked')
async def poof(ctx, world=None):
    
    if str(world) not in load_f2p_worlds():
        await ctx.send('All I am asking for is for you to enter a valid F2P world. I beg you.')
        return
    
    #remove star from .json
    loc, tier = remove_star(world, 'active_stars.json', output_data=True)
    
    if loc is None:
        await ctx.send(f'Either an unexpected error has occurred OR there was no active world listed for {world}! The current wave time is +{get_wave_time()}.')
        return
    
    wave_time = get_wave_time()
    
    await ctx.send(f"⭐ Confirming poof of star \nWorld: {world}\nLoc: {loc}\nTier: {tier}\nThe current wave time is +{wave_time}")
    
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
    
    tier = remove_frontal_corTex(tier)

    #load list of f2p worlds
    f2p_world_list = load_f2p_worlds()
    
    if (str(world) not in f2p_world_list) | (int(tier)>9) | (int(tier)<1):
        await ctx.send(print_error_message(command='call')+'\n'+'-# Use your noggin next time.')
        return

    #if an entry with the same f2p world is not already in the .json file, add it!
    world_check = world_check_flag(world, filename='active_stars.json')
    
    if world_check:
        await ctx.send(f'A star for world {world} is already listed!')
        return

    #remove star from the $backups list!
    remove_star(world, 'held_stars.json')
    
    try:
        #cancel the job once done
        job_id = f"hold_{world}_{tier}"
        scheduler.remove_job(job_id)
        print(f'Job ID {job_id} removed.')
    except:
        print(f'Called star in world {world} was not a backup; no job to remove.')
    
    #add star to .json
    username = ctx.author.name
    user_id = ctx.author.id
    add_star_to_list(username, user_id, world, loc, tier, 'active_stars.json')

    await ctx.send(f"⭐ Star moved to $active list!\nWorld: {world}\nLoc: {loc}\nTier: {tier}")
        

@call.error
async def call_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(print_error_message(command='call')+'\n'+'-# Use your noggin next time.')
    else:
        raise error
        
        
############################################################
#In a channel of your choosing, type command and the bot will post
#list of active stars every x minutes
#use: 
#   $start_active_loop [minutes]
#e.g., '$start_active_loop 30' will print the list every 30 minutes in the channel
############################################################
@bot.command(help='Sets up the bot to send $active list in the designated channel every N minutes, where N is an integer. Restricted to @Mods role.\nExample usage: $start_active_loop N')
@commands.has_role('Mods')

#registers this function as a bot command that is called when user types $start_active_loop
async def start_active_loop(ctx,minutes=10):
    
    #unique identifier for a Discord SERVER
    guild_id = ctx.guild.id
    #unique identifier for a Discord CHANNEL
    channel_id = ctx.channel.id
    
    #associates server ID with the channel ID
    scheduled_channel_ids_active[guild_id] = channel_id

    await ctx.send(f"The Active Stars post will be updated in this channel every {minutes} minute(s)!")
    
    #NOTE: message_id=123 is a PLACEHOLDER. If I do not define it at all, the default is message_id=None and the
    #code will not output a message_id (which I need for $start_active_loop)
    message_id = await send_embed('active_stars.json', ctx.channel, active=True, hold=False, message_id=123)    
        
    #scheduler functions must be non-async functions)
    #this function will schedule the async (send_message()) to run inside of the Discord bot's
    #event loop, even if APScheduler triggers it from a different thread
    def run_job():
        embed_list = asyncio.run_coroutine_threadsafe(send_embed('active_stars.json',
                                                                 bot.get_channel(channel_id),
                                                                 active=True,hold=False,
                                                                 message_id=message_id),
                                                      bot.loop)
    
    #creates job id given the server! this way, I can have multiple jobs for multiple servers :-)
    job_id = f"scheduled_msg_active_{guild_id}"    

    #only add job if it hasn't been added yet
    #this *actually* schedules the event!
    if not scheduler.get_job(job_id):
        #use scheduler that we defined at for on_ready()
        scheduler.add_job(run_job, trigger='interval', minutes=minutes, id=job_id)    

    #save to JSON so it persists (i.e., not wiped from memory when main.py is terminated)
    all_jobs = load_json_file('keyword_lists/scheduled_active_jobs.json')   #if .json already exists, load
    
    #write the new job (corresponding to guild_id) and save channel_id, interval, message_id)
    all_jobs[str(guild_id)] = {
        'channel_id': scheduled_channel_ids_active[guild_id],
        'interval': minutes,
        'message_id': message_id
    }
        
    save_json_file(all_jobs, 'keyword_lists/scheduled_active_jobs.json')

############################################################
#In the same channel as above, type command and bot will cease typing
#the list of active stars at the indicated time interval
#use: 
#   $stop_active_loop
############################################################
@bot.command(help="Terminates the bot's sending of $active list in the designated channel every N minutes, if applicable. Restricted to @Mods role.\nExample usage: $stop_active_loop")
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
#Print list of worlds in order from early- to late-wave spawns
#Will remove any worlds currently harboring stars, per $active
#Outputs comma-separated list to paste into Runelite plugin
#use: 
#   $hoplist
############################################################    
@bot.command(help='Prints comma-separated world list in order of early- to late- wave spawns. Filters out $active worlds.\nExample usage: $hoplist')
async def hoplist(ctx):
    hoplist_text = generate_hoplist_text()
    await ctx.send(hoplist_text)
    #ezpz!

############################################################
#In a channel of your choosing, type command and the bot will post
#list of filtered f2p worlds in order of early-to-late-to-no poof time
#use: 
#   $start_hop_loop [minutes]
#e.g., '$start_hop_loop 30' will print the list every 30 minutes in the channel
############################################################    
@bot.command(help='Sets up the bot to send a filtered list of f2p worlds, in order of early-to-late-to-no poof time, in the designated channel every N minutes (where N is an integer). Restricted to @Mods role.\nExample usage: $start_hop_loop N')
@commands.has_role('Mods')

#registers this function as a bot command that is called when user types $start_hop_loop
async def start_hop_loop(ctx,minutes=10):
    
    #unique identifier for a Discord SERVER
    guild_id = ctx.guild.id
    #unique identifier for a Discord CHANNEL
    channel_id = ctx.channel.id
    
    #associates server ID with the channel ID
    scheduled_channel_ids_hoplist[guild_id] = channel_id

    #post a fun little confirmation message. wouldn't want the laddies and lassies to think nothing happened.
    await ctx.send(f"The Hop List post below will be updated in this channel every {minutes} minute(s)!")
    
    #initialize the loop message...and define the unique message id to ensure the same message is edited every time
    loop_message = await ctx.send(generate_hoplist_text())
    message_id = loop_message.id
    
    async def send_message(channel, message_id):
        text = generate_hoplist_text()
        try:
            msg = await channel.fetch_message(message_id)
            await msg.edit(content=text)
        except discord.NotFound:
            await channel.send(text)

    
    #define the job function to schedule...
    def run_job():
        #schedule coroutine safely inside the bot loop
        asyncio.run_coroutine_threadsafe(
            send_hoplist_message(bot.get_channel(channel_id), message_id),
            bot.loop
        )
    
    #creates job id given the server! this way, I can have multiple jobs for multiple servers :-)
    job_id = f"scheduled_msg_hoplist_{guild_id}"    

    #only add job if it hasn't been added yet
    #this *actually* schedules the event!
    if not scheduler.get_job(job_id):
        #use scheduler that we defined at for on_ready()
        scheduler.add_job(run_job, trigger='interval', minutes=minutes, id=job_id)    

    #save to JSON so it persists (i.e., not wiped from memory when main.py is terminated)
    all_jobs = load_json_file('keyword_lists/scheduled_hoplist_jobs.json')   #if .json already exists, load
    
    #write the new job (corresponding to guild_id) and save channel_id, interval, message_id)
    all_jobs[str(guild_id)] = {
        'channel_id': scheduled_channel_ids_hoplist[guild_id],
        'interval': minutes,
        'message_id': message_id
    }
        
    save_json_file(all_jobs, 'keyword_lists/scheduled_hoplist_jobs.json')    
    
    
############################################################
#In the same channel as above, type command and bot will cease typing
#the f2p world hoplist at the indicated time interval
#use: 
#   $stop_hop_loop
############################################################
@bot.command(help="Terminates the bot's sending of $hoplist in the designated channel every N minutes, if applicable. Restricted to @Mods role.\nExample usage: $stop_hop_loop")
@commands.has_role('Mods')
async def stop_hop_loop(ctx):
    
    #get server ID
    guild_id = ctx.guild.id
    
    #pull the job id (again, given the server id)
    job_id = f"scheduled_msg_hoplist_{ctx.guild.id}"
    
    #if $stop_hop_loop, then remove the job if said job exists.
    job = scheduler.get_job(job_id)
    if job:
        job.remove()
        await ctx.send("The posting of the hoplist in this channel has been terminated.")
    else:
        await ctx.send("There's no hoplist scheduled message.")
    
    #remove job from the the dictionary! that is...clear from memory.
    #if guild_id not found, the "None" ensures there is no output error message in terminal
    scheduled_channel_ids_hoplist.pop(guild_id, None)
    #load all jobs .json file
    all_jobs = load_json_file('keyword_lists/scheduled_hoplist_jobs.json')
    #remove the job associated with the server!
    all_jobs.pop(str(guild_id), None)
    #re-write .json file
    save_json_file(all_jobs, 'keyword_lists/scheduled_hoplist_jobs.json')    

    
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
    

################################################################################
################################################################################
################################################################################    
    
    
bot.run(os.getenv('TOKEN'))