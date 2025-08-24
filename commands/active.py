############################################################
#print list of current active stars in an aesthetic textbox
#use: 
#   $active
############################################################     


from discord.ext import commands
import sys

sys.path.insert(0, '../utils')
from embed_utils import send_embed


class Active(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Prints list of active stars.\nExample usage: $active')
    async def active(self, ctx):
        await send_embed('active_stars.json', ctx, active=True)
        
async def setup(bot):
    await bot.add_cog(Active(bot))