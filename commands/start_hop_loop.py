############################################################
#In a channel of your choosing, type command and the bot will post
#list of filtered f2p worlds in order of early-to-late-to-no poof time
#use: 
#   $start_hop_loop [minutes]
#e.g., '$start_hop_loop 30' will print the list every 30 minutes in the channel
############################################################  

from discord.ext import commands
import asyncio
import sys
import discord

sys.path.insert(0, '../utils')
from hoplist_utils import generate_hoplist_text, send_hoplist_message
from scheduler_utils import scheduler
from universal_utils import load_json_file, save_json_file


class Hop_Loop(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Sets up the bot to send a filtered list of f2p worlds, in order of early-to-late-to-no poof time, in the designated channel every N minutes (where N is an integer). Restricted to @Mods role.\nExample usage: $start_hop_loop N')
    @commands.has_role('Mods')

    #registers this function as a bot command that is called when user types $start_hop_loop
    async def start_hop_loop(self, ctx, minutes=10):

        #validate minutes
        minutes = max(int(minutes), 1)

        #unique identifier for a Discord SERVER
        guild_id = ctx.guild.id
        #unique identifier for a Discord CHANNEL
        channel_id = ctx.channel.id

        #post a fun little confirmation message. wouldn't want the laddies and lassies to think nothing happened.
        await ctx.send(f"The Hop List post below will be updated in this channel every {minutes} minute(s)!")

        #initialize the loop message...and define the unique message id to ensure the same message is edited every time
        loop_message = await ctx.send(generate_hoplist_text())
        message_id = loop_message.id

        #define the job function to schedule...
        def run_job():
            #schedule coroutine safely inside the bot loop
            asyncio.run_coroutine_threadsafe(
                send_hoplist_message(self.bot.get_channel(channel_id), message_id),
                self.bot.loop
            )

        #creates job id given the server! this way, I can have multiple jobs for multiple servers :-)
        job_id = f"scheduled_msg_hoplist_{guild_id}"    

        #only add job if it hasn't been added yet
        #this *actually* schedules the event!
        if not scheduler.get_job(job_id):
            #use scheduler that we defined at for on_ready()
            scheduler.add_job(run_job, trigger='interval', minutes=minutes, id=job_id, misfire_grace_time=30)    

        #save to JSON so it persists (i.e., not wiped from memory when main.py is terminated)
        all_jobs = load_json_file('scheduled_jobs/scheduled_hoplist_jobs.json')   #if .json already exists, load

        #write the new job (corresponding to guild_id) and save channel_id, interval, message_id)
        all_jobs[str(guild_id)] = {
            'channel_id': channel_id,
            'interval': minutes,
            'message_id': message_id
        }

        save_json_file(all_jobs, 'scheduled_jobs/scheduled_hoplist_jobs.json')    
        
async def setup(bot):
    await bot.add_cog(Hop_Loop(bot))