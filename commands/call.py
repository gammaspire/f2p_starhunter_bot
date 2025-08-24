############################################################
#add active star to the .json list
#use: 
#   $call world loc tier
#e.g., 
#   $call 308 akm 8
############################################################  

from discord.ext import commands
import sys

sys.path.insert(0, '../utils')
from scheduler_utils import scheduler
from universal_utils import remove_frontal_corTex, load_f2p_worlds, world_check_flag
from star_utils import print_error_message, add_star_to_list, remove_star


class Call(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Calls star and moves to $active list. Restricted to @Ranked role.\nExample usage: $call 308 akm 8')
    @commands.has_role('Ranked')
    async def call(self, ctx, world, loc, tier):

        tier = remove_frontal_corTex(tier)

        #load list of f2p worlds
        f2p_world_list = load_f2p_worlds()

        if (str(world) not in f2p_world_list) or (int(tier)>9) or (int(tier)<1):
            await ctx.send(print_error_message(command='call')+'\n'+'-# Use your noggin next time.')
            return

        #if an entry with the same f2p world is not already in the .json file, add it!
        world_check = world_check_flag(world, filename='active_stars.json')

        if world_check:
            await ctx.send(f'A star for world {world} is already listed!')
            return

        #remove star from the $backups list!
        remove_star(world, 'held_stars.json')

        try:
            #cancel the job once done
            job_id = f"hold_{world}_{tier}"
            scheduler.remove_job(job_id)
            print(f'Job ID {job_id} removed.')
        except:
            print(f'Called star in world {world} was not a backup; no job to remove.')

        #add star to .json
        username = ctx.author.name
        user_id = ctx.author.id
        add_star_to_list(username, user_id, world, loc, tier, 'active_stars.json')

        await ctx.send(f"⭐ Star moved to $active list!\nWorld: {world}\nLoc: {loc}\nTier: {tier}")
     
    
async def setup(bot):
    await bot.add_cog(Call(bot))