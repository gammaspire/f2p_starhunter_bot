############################################################
#In the same channel in which $start_active_loop was run, type this command and 
#bot will cease typing the list of active stars at the indicated time interval
#use: 
#   $stop_active_loop
############################################################

from discord.ext import commands
import sys

sys.path.insert(0, '../utils')
from scheduler_utils import scheduler
from universal_utils import load_json_file, save_json_file

class Stop_Active(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Terminates the bot's sending of $active list in the designated channel every N minutes, if applicable. Restricted to @Mods role.\nExample usage: $stop_active_loop")
    @commands.has_role('Mods')
    async def stop_active_loop(self, ctx):

        try:
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

            #load all jobs .json file
            all_jobs = load_json_file('scheduled_jobs/scheduled_active_jobs.json')
            #remove the job associated with the server!
            all_jobs.pop(str(guild_id), None)
            #re-write .json file
            save_json_file(all_jobs, 'scheduled_jobs/scheduled_active_jobs.json')

        except Exception as e:
            # print full traceback if anything fails
            import traceback
            traceback.print_exc()  
          
        
async def setup(bot):
    await bot.add_cog(Stop_Active(bot))