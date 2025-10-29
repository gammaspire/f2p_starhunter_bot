############################################################
#In a channel of your choosing, type command and the bot will post
#list of active stars every x minutes
#use: 
#   $start_active_loop [minutes]
#e.g., '$start_active_loop 30' will print the list every 30 minutes in the channel
############################################################


from discord.ext import commands
import asyncio
from discord import app_commands, Interaction

from embed_utils import send_embed
from scheduler_utils import scheduler
from universal_utils import load_json_file, save_json_file

from config import GUILD, MOD_ROLE_NAME


class Start_Active(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    #look! another helper function! 
    async def _start_loop(self, channel, guild_id, minutes, send_func):
        
        #check if the job_id already exists...
        job_id = f"scheduled_msg_active_{guild_id}"
        if scheduler.get_job(job_id):
            await send_func('There is already an Active Loop running in this server!')
            return
        
        #validate minutes input
        if minutes < 1:
            await send_func("Interval must be at least 1 minute.")
            return
        
        try:
            #unique identifier for a Discord CHANNEL
            channel_id = channel.id

            #notify user which channel will receive updates
            await send_func(f"The Active Stars post will be updated in this channel every {minutes} minute(s)!")

            #send the initial embed and get its message ID
            embed_msg = await send_embed('active_stars.json', channel, active=True, hold=False)
            message_id = embed_msg.id  

            #scheduler functions must be non-async functions
            #this function will schedule the async (send_embed()) to run inside of the Discord bot's
            #event loop, even if APScheduler triggers it from a different thread
            def run_job():
                try:
                    asyncio.run_coroutine_threadsafe(
                        send_embed('active_stars.json', self.bot.get_channel(channel_id), active=True, hold=False,
                                   message_id=message_id),
                        self.bot.loop)
                except Exception as e:
                    print(f"[Error] Failed to update Active Stars embed: {e}")

            #creates job ID given the server! this way, I can have multiple jobs for multiple servers :-)
            job_id = f"scheduled_msg_active_{guild_id}"    

            #only add job if it hasn't been added yet
            #this *actually* schedules the event!
            if not scheduler.get_job(job_id):
                scheduler.add_job(run_job, trigger='interval', minutes=minutes, id=job_id, misfire_grace_time=30)

            #if .json already exists, load it
            all_jobs = load_json_file('scheduled_jobs/scheduled_active_jobs.json') or {}  

            # write the new job (corresponding to guild_id) and save channel_id, interval, message_id
            all_jobs[str(guild_id)] = {
                'channel_id': channel_id,
                'interval': minutes,
                'message_id': message_id}

            #save to JSON so it persists (i.e., not wiped from memory when main.py is terminated)
            save_json_file(all_jobs, 'scheduled_jobs/scheduled_active_jobs.json')

        except Exception as e:
            #print full traceback if anything fails
            print(e)  
    
    ############################################################
    #prefix command: $start_active_loop
    ############################################################
    @commands.command(help=f'Sets up the bot to send active list in the designated channel every N minutes, where N is an integer. Restricted to @{MOD_ROLE_NAME} role.\nPrefix example: $start_active_loop 5')
    @commands.has_role(MOD_ROLE_NAME)

    #registers this function as a bot command that is called when user types $start_active_loop
    async def start_active_loop(self, ctx, minutes=5):
        await self._start_loop(ctx.channel, ctx.guild.id, minutes, ctx.send)
        
    ############################################################
    #slash command: /start_active_loop
    ############################################################
    @app_commands.command(name='start_active_loop',
        description=f'Sends/updates the active star list in the designated channel every N minutes. Restricted to @{MOD_ROLE_NAME}.')
    @app_commands.checks.has_role(MOD_ROLE_NAME)
    async def start_active_loop_slash(self, interaction: Interaction, minutes: int = 5):

        #send_func will only ever send the confirmation text. send_embed() does the rest!
        async def send_func(msg: str):
            if not interaction.response.is_done():
                await interaction.response.send_message(msg)
            else:
                await interaction.response.send_message(msg)

        #this handles the embed posting + loop scheduling
        await self._start_loop(interaction.channel, interaction.guild_id, minutes, send_func)
    
#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Start_Active.atart_active_loop_slash = app_commands.guilds(GUILD)(Start_Active.start_active_loop_slash)   

async def setup(bot):
    await bot.add_cog(Start_Active(bot))