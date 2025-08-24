############################################################
#hold star in held_stars.json file until time to release
#use: 
#   $hold world loc tier
#e.g., 
#   $hold 308 nc 8
############################################################

import asyncio
from discord.ext import commands
import sys

from discord_ui import CallStarView   #my CallStarView class lives here

sys.path.insert(0, '../utils')
from scheduler_utils import scheduler  #import my global scheduler instance
from universal_utils import load_f2p_worlds, remove_frontal_corTex, world_check_flag
from googlesheet_utils import check_wave_call
from star_utils import print_error_message, add_star_to_list, load_loc_dict


#creating a Cog class (yay!), which will enable me to create this hold.py file and not include it in main.py :-)
class Hold(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Records given world, loc, and tier into the $backups list.\nExample usage: $hold 308 akm 8')
    async def hold(self, ctx, world=None, loc=None, tier=None):

        username = ctx.author.name
        user_id = ctx.author.id

        #check if user remembered to include world, loc, and tier arguments
        if not world or not loc or not tier:
            await ctx.send(print_error_message(command='hold'))
            await ctx.send('-# Come on, now. You should know better.')
            return

        try:
            #now check if the world is f2p; if not, goodbye.
            if (str(world) not in load_f2p_worlds()):
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


async def setup(bot):
    await bot.add_cog(Hold(bot))