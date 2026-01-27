############################################################
#add active star to the .json list
#use: 
#   $call world loc tier
#e.g., 
#   $call 308 akm 8
############################################################  

from discord.ext import commands
from discord import app_commands, Interaction

from config import GUILD, RANKED_ROLE_NAME

from scheduler_utils import scheduler
from universal_utils import remove_frontal_corTex, load_f2p_worlds, world_check_flag, load_poof_cache, fetch_poof
from star_utils import print_error_message, add_star_to_list, remove_star


def call_checks(world, loc, tier):
    
    if world is None or tier is None:
        message = print_error_message(command='call')+'\n'+'-# Use your noggin next time.'
        return [True, message]
    
    #load list of f2p worlds
    f2p_world_list = load_f2p_worlds()

    if (str(world) not in f2p_world_list) or (int(tier)>9) or (int(tier)<1):
        message = print_error_message(command='call')+'\n'+'-# Use your noggin next time.'
        return [True, message]
    
    #if an entry with the same f2p world is not already in the .json file, add it!
    world_check = world_check_flag(world, filename='active_stars.json')

    if world_check:
        message = f'A star for world {world} is already listed!'
        return [True, message]
    
    return [False, None]


class Call(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    ############################################################
    #prefix command: $call
    ############################################################
    @commands.command(help=f'Calls star and moves to $active list. Restricted to @{RANKED_ROLE_NAME} role.\nPrefix Example: $call 308 akm 8')
    @commands.has_role(RANKED_ROLE_NAME)
    async def call(self, ctx, world=None, loc=None, tier=None):
        
        #a few...quality checks
        check_list = call_checks(world, loc, tier)
        
        #if the first element is True, then print the error message (send element) and terminate the function
        if check_list[0]:
            await ctx.send(check_list[1])
            return
        
        tier = remove_frontal_corTex(tier)
        
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
        username = ctx.author.display_name
        user_id = ctx.author.id
        poof_cache = load_poof_cache()
        poof_time = fetch_poof(poof_cache, world)
        add_star_to_list(username, user_id, world, loc, tier, 
                         call_time_unix=None, poof_time=poof_time, filename='active_stars.json')

        await ctx.send(f"⭐ Star moved to $active list!\nWorld: {world}\nLoc: {loc}\nTier: {tier}")

    ############################################################
    #slash command: /call
    ############################################################    
    @app_commands.command(name="call", description="Calls star [F2P world, loc shorthand, Tier 1-9] and moves to the active list.") 
    @app_commands.checks.has_role(RANKED_ROLE_NAME)
    async def call_slash(self, interaction: Interaction, world : str, loc : str, tier: str):
        
        #a few...quality checks
        check_list = call_checks(world, loc, tier)
        
        if check_list[0]:
            await interaction.response.send_message(check_list[1])
            return
        
        tier = remove_frontal_corTex(tier)

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
        author = interaction.user
        username = author.display_name
        user_id = author.id
        poof_cache = load_poof_cache()
        poof_time = fetch_poof(poof_cache, world)
        add_star_to_list(username, user_id, world, loc, tier, 
                         call_time_unix=None, poof_time=poof_time, filename='active_stars.json')

        await interaction.response.send_message(f"⭐ Star moved to $active list!\nWorld: {world}\nLoc: {loc}\nTier: {tier}")
            
#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Call.call_slash = app_commands.guilds(GUILD)(Call.call_slash)    

async def setup(bot):
    await bot.add_cog(Call(bot))