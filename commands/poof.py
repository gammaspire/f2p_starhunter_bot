############################################################
#manually remove active star from the list
#use: 
#   $poof f2p_world
#e.g., 
#   $poof 308
############################################################        

from discord.ext import commands
import sys

sys.path.insert(0, '../utils')
from scheduler_utils import scheduler
from universal_utils import load_f2p_worlds
from googlesheet_utils import get_wave_time
from star_utils import add_star_to_list, remove_star


class Poof(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Manually removes star from $active list (HOWEVER -- if star is still active on SM, it will not be removed). Restricted to @Ranked role.\nExample usage: $poof 308')
    @commands.has_role('Ranked')
    async def poof(self, ctx, world=None):

        if str(world) not in load_f2p_worlds():
            await ctx.send('All I am asking for is for you to enter a valid F2P world. I beg you.')
            return

        #remove star from .json
        loc, tier = remove_star(world, 'active_stars.json', output_data=True)

        if loc is None:
            await ctx.send(f'Either an unexpected error has occurred OR there was no active world listed for {world}! The current wave time is +{get_wave_time()}.')
            return

        wave_time = get_wave_time()

        await ctx.send(f"⭐ Confirming poof of star \nWorld: {world}\nLoc: {loc}\nTier: {tier}\nThe current wave time is +{wave_time}")
        

async def setup(bot):
    await bot.add_cog(Poof(bot))