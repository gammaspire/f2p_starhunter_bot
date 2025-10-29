############################################################
#hold star in held_stars.json file until time to release
#use: 
#   $hold world loc tier
#e.g., 
#   $hold 308 nc 8
############################################################

import asyncio
from discord.ext import commands
from discord import app_commands, Interaction, utils

from scheduler_utils import scheduler  #import my global scheduler instance
from universal_utils import load_f2p_worlds, remove_frontal_corTex, world_check_flag, get_star_holder
from googlesheet_utils import check_wave_call
from star_utils import print_error_message, add_star_to_list, load_loc_dict

from config import GUILD, GUILD_VALUE, RANKED_ROLE_NAME

from call_button import CallStarView   #my 'call star' button lives here


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
    
    if int(tier) <= 0:
        message = f'-# I know I am now holding stars with tiers lower than 6, but could you maybe *not* with your juvenile attempts at trickery? Are you that desperate for a "gotcha!" moment? Do you swipe pacifiers from infants, too? Get real.'
        return [True, message]
    
    #check if the world is already held or called
    if world_check_flag(world, filename='held_stars.json'):
        message = f'There is already a held star for world {world}.'
        return [True, message]
    if world_check_flag(world, filename='active_stars.json'):
        message = f'There is already an active star for world {world}.'
        return [True, message]
    
    #tier *should* be between 6 and 9
    if not (6 <= int(tier) <= 9):
        message = f'-# You really want to hold a t{tier} star? Good heavens, whatever.'
        return [False, message]

    return [False, None]


class Hold(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    #the _ in front is a naming convention to signal that function is only to be used within the class!
    async def _process_hold(self, user, world, loc, tier, send_func):
        """Shared logic for holding/calling stars; send_func can be ctx.send or interaction.response/followup.send"""
        
        username = user.display_name
        user_id = user.id

        tier = remove_frontal_corTex(tier)
        
        hold_check = hold_checks(world, loc, tier)

        #if error (flag is True), send message and stop
        if hold_check[0]:
            await send_func(hold_check[1])
            return

        #load our location shorthand dictionary
        loc_dict = load_loc_dict()

        try:
            #if it is indeed time to call the star, CALL THE STAR
            #compares wave time and eow suggested call time for star
            if await check_wave_call(world, tier):
                view = CallStarView(username, user_id, world, loc, tier)   #create the view
                #just ping the user who sent the message. they will figure it out.
                msg = await send_func(f"<⭐ {user.mention}> CALL STAR: World {world}, {loc}, Tier {tier}",
                                      view=view)
                view.message = msg   #store the message so timeout can disable buttons
                return

            #lastly...if none of the above checks terminated the function, hold the star~
            add_star_to_list(username, user_id, world, loc, tier, filename='held_stars.json')
            
            #add the held message
            if hold_check[1] is None:
                msg = await send_func(f"Holding the following ⭐:\nWorld: {world}\nLoc: {loc}\nTier: {tier}")
            else:
                msg = await send_func(f"Holding the following ⭐:\nWorld: {world}\nLoc: {loc}\nTier: {tier}\n"
                                      f"{hold_check[1]}")
                
            #schedule the checking job; if star is ready to call, remove job!
            async def monitor_star():

                #if the world is in the active list, REMOVE THE SCHEDULED JOB.
                if world_check_flag(world, filename='active_stars.json'):
                    job_id = f"hold_{world}_{tier}"  #unique job ID
                    scheduler.remove_job(job_id)     #cancel the job
                    await send_func(f"⭐ HELD STAR World {world} {loc} t{tier} is now in the active stars list and has automatically been removed from backups.")
                    return

                #if world is not in active list, re-check the call eligibility
                call_flag = await check_wave_call(world, tier)

                if call_flag:
                    try:
                        #pull the guild...
                        guild = await self.bot.fetch_guild(GUILD_VALUE)
                        
                        #first: GRAB THE USER WHO IS IN THE HELD STAR .JSON FILE FOR THAT WORLD!
                        #this is needed so bot-kun will ping the correct user!
                        holder_entry = get_star_holder(world)
                        
                        holder_id = int(holder_entry.get("user_id"))  #get ID of user who held the star!
                        holder_obj = await guild.fetch_member(holder_id)  #get ID of user who held star
                                                                          #or was later assigned to call the star
                        
                        #grab the ranked role!
                        ranked_role = utils.get(guild.roles, name=RANKED_ROLE_NAME)
                        
                        #now...if the user who held the star is not ranked, ping @Ranked instead of @user!
                        #otherwise, ping the user
                        if ranked_role not in holder_obj.roles:
                            holder_mention = ranked_role.mention if ranked_role else f"@{RANKED_ROLE_NAME}"
                        else:
                            holder_mention = holder_obj.mention
                                                
                        if hold_check[1] is None:     #check if hold_check[1] has a message. if so, then the user
                                                      #deserves to be reprimanded for holding a dinky star.
                            full_call_message = f"<⭐ {holder_mention}> CALL STAR: World {world}, {loc}, Tier {tier}"
                        else:
                            full_call_message = f"<⭐ {holder_mention}> CALL STAR: World {world}, {loc}, Tier {tier}\n-# I can't believe I have to actually ping you for a dinky star."

                        #this will post the holder from held_stars.json in the /active list.
                        view = CallStarView(holder_obj.display_name, holder_id, world, loc, tier)
                        msg = await send_func(full_call_message, view=view)
                        view.message = msg
                    except Exception as e:
                        print(e)

                    job_id = f"hold_{world}_{tier}"  #unique job ID
                    scheduler.remove_job(job_id)     #cancel job

            #non-async wrapper for the scheduler
            def run_job():
                asyncio.run_coroutine_threadsafe(monitor_star(), self.bot.loop)

            job_id = f"hold_{world}_{tier}"
            if not scheduler.get_job(job_id):
                scheduler.add_job(run_job, 'interval', minutes=2, id=job_id, misfire_grace_time=30)

        except Exception as e:
            import traceback
            traceback.print_exc()


    ############################################################
    #prefix command: $hold
    ############################################################
    @commands.command(help='Records given world, loc, and tier into the list of backup stars.\nPrefix example: $hold 308 akm 8')
    async def hold(self, ctx, world=None, loc=None, tier=None):
        # ctx.send returns the message object — needed for views
        async def send_func(*args, **kwargs):
            return await ctx.send(*args, **kwargs)
        
        await self._process_hold(ctx.author, world, loc, tier, send_func)


    ############################################################
    #slash command: /hold
    ############################################################
    @app_commands.command(name="hold", description="Records given world, loc, and tier into the backups list")  
    async def hold_slash(self, interaction: Interaction, world: str, loc: str, tier: str):
        await interaction.response.defer()  #acknowledge the command right away so that it does not 
                                            #break if /hold takes longer than 3 seconds to complete
        
        channel = interaction.channel
        
        # must return the message object when sending
        async def send_func(message: str = None, **kwargs):
            return await channel.send(message, **kwargs)

        await self._process_hold(interaction.user, world, loc, tier, send_func)
        
        await interaction.followup.send("Confirming...")
        
#attaching a decorator to a function after the class is defined...
if GUILD is not None:
    Hold.hold_slash = app_commands.guilds(GUILD)(Hold.hold_slash)   

async def setup(bot):
    await bot.add_cog(Hold(bot))