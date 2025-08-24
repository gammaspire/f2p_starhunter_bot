############################################################
#print list of current backup stars in an aesthetic textbox
#use: 
#   $backups
############################################################  

from discord.ext import commands
import sys

sys.path.insert(0, '../utils')
from embed_utils import send_embed


class Backups(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(help='Prints list of backup worlds. Restricted to @Ranked role.\nExample usage: $backups')
    @commands.has_role('Ranked')
    async def backups(self, ctx):
        try:
            await send_embed('held_stars.json', ctx, hold=True)
        except Exception as e:
            await ctx.send(f"Error loading backup stars: {e}.")


async def setup(bot):
    await bot.add_cog(Backups(bot))