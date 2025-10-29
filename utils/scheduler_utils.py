import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import json

from pull_f2p_worlds import pull_f2p_worlds
from universal_utils import grab_job_ids, load_json_file

from embed_utils import send_embed
from hoplist_utils import send_hoplist_message


#global scheduler and dictionaries~
scheduler = AsyncIOScheduler()

#a quick function to return the scheduler for $hold
def get_scheduler():
    return scheduler

# --- JOB WRAPPERS ---
def run_active(bot, guild_id, channel_id, message_id):
    #try:
        channel = bot.get_channel(channel_id)
        if not channel:
            print(f"[run_active] Channel not found for guild {guild_id}, id {channel_id}")
            return

        asyncio.run_coroutine_threadsafe(
            send_embed("active_stars.json", channel, active=True, hold=False, message_id=message_id),
            bot.loop)
        
    #    try:
    #        result = future.result(timeout=5)
    #        print(f"[run_active] Coroutine completed successfully, result: {result}")
    #    except Exception as e:
    #        print(f"[run_active] Coroutine raised exception: {e}")
    #except Exception as e:
    #    print(f"[run_active] Exception in scheduling: {e}")


def run_hoplist(bot, guild_id, channel_id, message_id):
    channel = bot.get_channel(channel_id)
    asyncio.run_coroutine_threadsafe(
        send_hoplist_message(channel, message_id),
        bot.loop)

# --- SCHEDULER INITIALIZATION ---
def init_scheduler_jobs(bot):
    """Schedule pull_f2p_worlds and restore active/hoplist jobs."""

    scheduler.start()

    # --- Pull F2P worlds job ---
    job_id = "pull_f2p_worlds_job"
    if not scheduler.get_job(job_id):
        scheduler.add_job(pull_f2p_worlds, 'interval', hours=24, id=job_id, 
                          replace_existing=False, next_run_time=datetime.now())
        
        print("Pull F2P worlds job is successfully scheduled to run once per 24 hours!")

    # --- Restore ACTIVE jobs ---
    active_jobs = load_json_file('scheduled_jobs/scheduled_active_jobs.json')
    for guild_id, job_info in active_jobs.items():
        guild_id = int(guild_id)
        channel_id, minutes, message_id = grab_job_ids(job_info)

        job_id = f"scheduled_msg_active_{guild_id}"
        if not scheduler.get_job(job_id):
            scheduler.add_job(run_active, trigger='interval', minutes=minutes, id=job_id, 
                              args=[bot, guild_id, channel_id, message_id])
            print(f"Restored active star messages for guild {guild_id} every {minutes} minutes.")

    # --- Restore HOPLIST jobs ---
    hoplist_jobs = load_json_file('scheduled_jobs/scheduled_hoplist_jobs.json')
    for guild_id, job_info in hoplist_jobs.items():
        guild_id = int(guild_id)
        channel_id, minutes, message_id = grab_job_ids(job_info)

        job_id = f"scheduled_msg_hoplist_{guild_id}"
        if not scheduler.get_job(job_id):
            scheduler.add_job(run_hoplist, trigger='interval', minutes=minutes, id=job_id, 
                              args=[bot, guild_id, channel_id, message_id])
            print(f"Restored hoplist messages for guild {guild_id} every {minutes} minutes.")

            
# --- RESET JSON FILES (needed for when restarting the  ---
def reset_star_jsons():
    """Clear held_stars.json and active_stars.json on bot startup."""
    for filename in ['keyword_lists/held_stars.json', 'keyword_lists/active_stars.json']:
        with open(filename, 'w') as f:
            json.dump([], f)
    print("Cleared held_stars.json and active_stars.json")