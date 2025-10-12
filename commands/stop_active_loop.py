from discord.ext import commands
from discord import app_commands, Interaction
import sys

sys.path.insert(0, '../utils')
from scheduler_utils import scheduler
from universal_utils import load_json_file, save_json_file

sys.path.insert(0, '../config')
from config import GUILD, MOD_ROLE_NAME

class Stop_Active(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    ############################################################
    # Prefix command
    ############################################################
    @commands.command(help=f"Terminates the bot's sending of $active list in the designated channel every N minutes, if applicable. Restricted to @{MOD_ROLE_NAME} role.\nExample usage: $stop_active_loop")
    @commands.has_role(MOD_ROLE_NAME)
    async def stop_active_loop(self, ctx):
        try:
            guild_id = ctx.guild.id
            job_id = f"scheduled_msg_active_{guild_id}"

            job = scheduler.get_job(job_id)
            if job:
                job.remove()
                await ctx.send("The posting of active stars in this channel has been terminated.")
            else:
                await ctx.send("There's no active scheduled message.")

            all_jobs = load_json_file('scheduled_jobs/scheduled_active_jobs.json')
            all_jobs.pop(str(guild_id), None)
            save_json_file(all_jobs, 'scheduled_jobs/scheduled_active_jobs.json')

        except Exception as e:
            import traceback
            traceback.print_exc()

    ############################################################
    # Slash command
    ############################################################
    @app_commands.command(name="stop_active_loop", description=f"Terminates the bot's sending of active stars every N minutes. Restricted to @{MOD_ROLE_NAME}.")
    @app_commands.checks.has_role(MOD_ROLE_NAME)
    async def stop_active_loop_slash(self, interaction: Interaction):
        try:
            guild_id = interaction.guild_id
            job_id = f"scheduled_msg_active_{guild_id}"

            job = scheduler.get_job(job_id)
            
            if job:
                job.remove()
                await interaction.response.send_message("The posting of active stars in this channel has been terminated.")
            else:
                await interaction.response.send_message("There is no active scheduled message.")

            all_jobs = load_json_file('scheduled_jobs/scheduled_active_jobs.json')
            all_jobs.pop(str(guild_id), None)
            save_json_file(all_jobs, 'scheduled_jobs/scheduled_active_jobs.json')

        except Exception as e:
            import traceback
            traceback.print_exc()

#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Stop_Active.stop_active_loop_slash = app_commands.guilds(GUILD)(Stop_Active.stop_active_loop_slash)   

async def setup(bot):
    await bot.add_cog(Stop_Active(bot))