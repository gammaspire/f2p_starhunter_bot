############################################################
#Print the current poof time estimate for a world!
#use: 
#   $poof_time world
#e.g., '$poof_time 308' will output '+30' if +30 is the poof time
############################################################

from discord.ext import commands
import sys

sys.path.insert(0, '../utils')
from universal_utils import load_f2p_worlds
from googlesheet_utils import get_wave_time, get_poof_time

#pull wave time and poof time for world. if world is recognized in the f2p world list, then
#print the poof time for the world, the current wave time, and whether the star is callable.
#otherwise, the print message will a default "World unknown", etc.
def create_poof_message(world_string):
    
    if str(world_string) not in load_f2p_worlds():
        return 'Error, likely because you are not using a valid F2P world. What a maroon.'
    
    poof_time = get_poof_time(world_string)

    #prints poof time for world and current wave time.

    if poof_time=='TBD':
        return f'Poof time for {world_string} is {poof_time}!'
    else:
        wave_time = get_wave_time()
        return f'Poof time for {world_string} is +{poof_time}. The current wave time is +{wave_time}.'
 

class Poof_Time(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(help='Prints poof time for the entered world.\nExample usage: $poof_time 308')
    async def poof_time(self, ctx, world):
        #load list of f2p worlds
        f2p_world_list = load_f2p_worlds()

        if world not in f2p_world_list:
            await ctx.send('Are you kidding? USE A VALID F2P WORLD.')
            return

        poof_message = create_poof_message(world)
        await ctx.send(poof_message)
  

async def setup(bot):
    await bot.add_cog(Poof_Time(bot))