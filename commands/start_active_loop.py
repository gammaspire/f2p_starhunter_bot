############################################################
#In a channel of your choosing, type command and the bot will post
#list of active stars every x minutes
#use: 
#   $start_active_loop [minutes]
#e.g., '$start_active_loop 30' will print the list every 30 minutes in the channel
############################################################


from discord.ext import commands
import sys
import asyncio

sys.path.insert(0, '../utils')
from embed_utils import send_embed
from scheduler_utils import scheduler
from universal_utils import load_json_file, save_json_file


class Start_Active(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(help='Sets up the bot to send $active list in the designated channel every N minutes, where N is an integer. Restricted to @Mods role.\nExample usage: $start_active_loop N')
    @commands.has_role('Mods')

    #registers this function as a bot command that is called when user types $start_active_loop
    async def start_active_loop(self, ctx, minutes=10):

        try:
            #validate minutes input
            if minutes < 1:
                await ctx.send("Interval must be at least 1 minute.")
                return

            #unique identifier for a Discord SERVER
            guild_id = ctx.guild.id
            #unique identifier for a Discord CHANNEL
            channel_id = ctx.channel.id

            #notify user which channel will receive updates
            await ctx.send(f"The Active Stars post will be updated in this channel every {minutes} minute(s)!")

            #send the initial embed and get its message ID
            embed_msg = await send_embed('active_stars.json', ctx.channel, active=True, hold=False)
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

            # creates job ID given the server! this way, I can have multiple jobs for multiple servers :-)
            job_id = f"scheduled_msg_active_{guild_id}"    

            # only add job if it hasn't been added yet
            # this *actually* schedules the event!
            if not scheduler.get_job(job_id):
                scheduler.add_job(run_job, trigger='interval', minutes=minutes, id=job_id, misfire_grace_time=30)

            # save to JSON so it persists (i.e., not wiped from memory when main.py is terminated)
            all_jobs = load_json_file('scheduled_jobs/scheduled_active_jobs.json') or {}  # if .json already exists, load it

            # write the new job (corresponding to guild_id) and save channel_id, interval, message_id
            all_jobs[str(guild_id)] = {
                'channel_id': channel_id,
                'interval': minutes,
                'message_id': message_id}

            save_json_file(all_jobs, 'scheduled_jobs/scheduled_active_jobs.json')

        except Exception as e:
            # print full traceback if anything fails
            import traceback
            traceback.print_exc()
            
async def setup(bot):
    await bot.add_cog(Start_Active(bot))