############################################################
#lost_worlds command which prints any inactive f2p worlds which still appear on dust.wiki
#use: 
#   $lost_worlds
############################################################  

from discord.ext import commands
import sys

sys.path.insert(0, '../utils')
from universal_utils import load_f2p_worlds

class Lost_Worlds(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(help='Prints this list of abridged help information.\nExample usage: $help')
    async def lost_worlds(self, ctx):
        try:
            _, omitted_worlds = load_f2p_worlds(output_omitted_worlds=True)
            await ctx.send(f'Here is a list of currently inactive F2P worlds:\n {omitted_worlds}')

        except:
            await ctx.send('Error pulling currently inactive F2P worlds. I guess you will have to use your eyeballs.')
     
    
async def setup(bot):
    await bot.add_cog(Lost_Worlds(bot))