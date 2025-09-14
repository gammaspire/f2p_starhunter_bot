############################################################
#In the same channel as above, type command and bot will cease typing
#the f2p world hoplist at the indicated time interval
#use: 
#   $stop_hop_loop
############################################################

from discord.ext import commands
from discord import app_commands, Interaction
import sys

sys.path.insert(0, '../utils')
from scheduler_utils import scheduler
from universal_utils import load_json_file, save_json_file

sys.path.insert(0, '../config')
from config import GUILD

class Stop_Hop(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
     
    #ANOTHER helper function.
    #remember that both the prefix and slash commands use this...helps avoid code duplication.
    async def _stop_hoplist_job(self, guild_id: int, send_func):
        #pull the job id (server-specific)
        job_id = f"scheduled_msg_hoplist_{guild_id}"

        #if job exists, remove it
        job = scheduler.get_job(job_id)
        if job:
            job.remove()
            await send_func("The posting of the hoplist in this channel has been terminated.")
        else:
            await send_func("There's no hoplist scheduled message.")

        #load jobs file
        all_jobs = load_json_file('scheduled_jobs/scheduled_hoplist_jobs.json')
        #remove the job associated with the server
        all_jobs.pop(str(guild_id), None)
        #overwrite jobs file
        save_json_file(all_jobs, 'scheduled_jobs/scheduled_hoplist_jobs.json')
    
    ############################################################
    # prefix command: $stop_hop_loop
    ############################################################
    @commands.command(help="Terminates the bot's sending of $hoplist in the designated channel every N minutes, if applicable. Restricted to @Mods role.\nExample usage: $stop_hop_loop")
    @commands.has_role('Mods')
    async def stop_hop_loop(self, ctx):
        await self._stop_hoplist_job(ctx.guild.id, ctx.send) 
        
    ############################################################
    # slash command: /stop_hop_loop
    ############################################################        
    @app_commands.command(name='stop_hop_loop', description='Terminates the hoplist loop in the designated channel. Restricted to @Mods.')
    @app_commands.checks.has_role('Mods')
    async def stop_hop_loop_slash(self, interaction: Interaction):
        await self._stop_hoplist_job(interaction.guild_id, interaction.response.send_message)

#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Stop_Hop.stop_hop_loop_slash = app_commands.guilds(GUILD)(Stop_Hop.stop_hop_loop_slash)   
    
async def setup(bot):
    await bot.add_cog(Stop_Hop(bot))