############################################################
#hold star in held_stars.json file until time to release
#use: 
#   $hold world loc tier
#e.g., 
#   $hold 308 nc 8
############################################################

import asyncio
from discord.ext import commands
from discord import app_commands, Interaction
import sys

from discord_ui import CallStarView   #my CallStarView class lives here

sys.path.insert(0, '../utils')
from scheduler_utils import scheduler  #import my global scheduler instance
from universal_utils import load_f2p_worlds, remove_frontal_corTex, world_check_flag
from googlesheet_utils import check_wave_call
from star_utils import print_error_message, add_star_to_list, load_loc_dict

sys.path.insert(0, '../config')
from config import GUILD


#check if the user-inputted star is 'holdable'!
def hold_checks(world, loc, tier):
    #check if user remembered to include world, loc, and tier arguments
    if not world or not loc or not tier:
        message = print_error_message(command='hold')+'\n'+'-# Come on, now. You should know better.'
        return [True, message]

    #now check if the world is f2p; if not, goodbye.
    if (str(world) not in load_f2p_worlds()):
        message = print_error_message(command='hold')+'\n'+'-# Derp.'
        return [True, message]

    #parse the tier...which must be between 6 and 9
    try:
        if not (6 <= int(tier) <= 9):
            message = f'-# You really wanted to hold a t{tier} star? Good heavens.'
            return [True, message]
    except:
        message = print_error_message(command='hold')
        return [True, message]

    #check if the world is already held or called
    if world_check_flag(world, filename='held_stars.json'):
        message = f'There is already a held star for world {world}.'
        return [True, message]
    if world_check_flag(world, filename='active_stars.json'):
        message = f'There is already an active star for world {world}.'
        return [True, message]

    return [False, None]


class Hold(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    #the _ in front is a naming convention to signal that function is only to be used within the class!
    async def _process_hold(self, user, world, loc, tier, send_func):
        """Shared logic for holding/calling stars; send_func can be ctx.send or interaction.response/followup.send"""
        
        username = user.name
        user_id = user.id

        tier = remove_frontal_corTex(tier)
        
        hold_check = hold_checks(world, loc, tier)

        #if error, send message and stop
        if hold_check[0]:
            await send_func(hold_check[1])
            return

        #load our location shorthand dictionary
        loc_dict = load_loc_dict()

        try:
            #if it is indeed time to call the star, CALL THE STAR
            #compares wave time and eow suggested call time for star
            if await check_wave_call(world, tier):
                await send_func(
                    f"<⭐ {user.mention}> CALL STAR: World {world}, {loc}, Tier {tier}",
                    view=CallStarView(username, user_id, world, loc, tier))   #CallStarView is a class
                return

            #lastly...if none of the above catches terminated the function, hold the star~
            add_star_to_list(username, user_id, world, loc, tier, filename='held_stars.json')
            await send_func(f"Holding the following ⭐:\nWorld: {world}\nLoc: {loc}\nTier: {tier}")

            #schedule the checking job; if star is ready to call, remove job!
            async def monitor_star():

                #if the world is in the $active list, REMOVE THE SCHEDULED JOB.
                if world_check_flag(world, filename='active_stars.json'):
                    #redefine the unique job_id
                    job_id = f"hold_{world}_{tier}"
                    #cancel the job
                    scheduler.remove_job(job_id)
                    await send_func(f"⭐ HELD STAR World {world} {loc} t{tier} is now in the $active list and has automatically been removed from $backups.")

                #if world is not in $active list, re-check the call eligibility
                call_flag = await check_wave_call(world, tier)

                if call_flag:

                    #view is what enables the button; will remove held star from .json when clicked and add to $active
                    try:
                        await send_func(
                            f"<⭐ {user.mention}> CALL STAR: World {world}, {loc}, Tier {tier}",
                            view=CallStarView(username, user_id, world, loc, tier))   #CallStarView is a class
                    except Exception as e:
                        print(e)

                    #redefine the unique job_id
                    job_id = f"hold_{world}_{tier}"
                    #cancel the job
                    scheduler.remove_job(job_id)

            #non-async wrapper for the scheduler
            def run_job():
                asyncio.run_coroutine_threadsafe(monitor_star(), self.bot.loop)

            #THE FUNCTIONS DEFINED ABOVE WILL RUN WITH THE LAST FEW LINES
            #unique job ID (based on user + star details)
            job_id = f"hold_{world}_{tier}"

            #will run run_job every two minutes!
            if not scheduler.get_job(job_id):
                scheduler.add_job(run_job, 'interval', minutes=2, id=job_id, misfire_grace_time=30)

        except Exception as e:
            import traceback
            traceback.print_exc()


    ############################################################
    #prefix command: $hold
    ############################################################
    @commands.command(help='Records given world, loc, and tier into the $backups list.\nPrefix example: $hold 308 akm 8')
    async def hold(self, ctx, world=None, loc=None, tier=None):
        await self._process_hold(ctx.author, world, loc, tier, ctx.send)  #last one is send_func


    ############################################################
    #slash command: /hold
    ############################################################
    @app_commands.command(name="hold", description="Records given world, loc, and tier into the backups list")  
    async def hold_slash(self, interaction: Interaction, world: str, loc: str, tier: str):
        await interaction.response.defer()  #acknowledge the command right away so that it does not 
                                            #break if /hold takes longer than 3 seconds to complete
        
        #after deferring, MUST use followup.send() for *all* messages
        await self._process_hold(interaction.user, world, loc, tier, interaction.followup.send)

#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Hold.hold_slash = app_commands.guilds(GUILD)(Hold.hold_slash)   

async def setup(bot):
    await bot.add_cog(Hold(bot))