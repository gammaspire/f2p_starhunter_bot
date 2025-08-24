############################################################
#In the same channel as above, type command and bot will cease typing
#the f2p world hoplist at the indicated time interval
#use: 
#   $stop_hop_loop
############################################################

from discord.ext import commands
import sys

sys.path.insert(0, '../utils')
from scheduler_utils import scheduler
from universal_utils import load_json_file, save_json_file



class Stop_Loop(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(help="Terminates the bot's sending of $hoplist in the designated channel every N minutes, if applicable. Restricted to @Mods role.\nExample usage: $stop_hop_loop")
    @commands.has_role('Mods')
    
    async def stop_hop_loop(self, ctx):

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

        #load all jobs .json file
        all_jobs = load_json_file('scheduled_jobs/scheduled_hoplist_jobs.json')
        #remove the job associated with the server!
        all_jobs.pop(str(guild_id), None)
        #re-write .json file
        save_json_file(all_jobs, 'scheduled_jobs/scheduled_hoplist_jobs.json')  
        
async def setup(bot):
    await bot.add_cog(Stop_Loop(bot))