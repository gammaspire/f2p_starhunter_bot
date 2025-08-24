############################################################
#Print list of worlds in order from early- to late-wave spawns
#Will remove any worlds currently harboring stars, per $active
#Outputs comma-separated list to paste into Runelite plugin
#use: 
#   $hoplist
############################################################  

from discord.ext import commands
import sys

sys.path.insert(0, '../utils')
from hoplist_utils import send_hoplist_message


class Hoplist(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help='Prints comma-separated world list in order of early- to late-wave spawns. '
             'Filters out $active worlds.\nExample usage: $hoplist'
    )
    async def hoplist(self, ctx):
        #sends the hoplist using the utility function, which handles formatting
        #'None' for message_id will make the function send a fresh message
        try:
            await send_hoplist_message(ctx.channel, None)
        except Exception as e:
            print(e)
        #ezpz!
        
async def setup(bot):
    await bot.add_cog(Hoplist(bot))