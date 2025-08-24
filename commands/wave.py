############################################################
#print current wave time into the chat!   
#use:
#    $wave
############################################################

from discord.ext import commands
from discord import Embed
import sys

sys.path.insert(0, '../utils')
from googlesheet_utils import get_wave_start_end


class Wave(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
            
    @commands.command(help='Prints real-time message of current wave start time, end time, and the wave time at which the message was sent.\nExample usage: $wave')
    async def wave(self, ctx):
        wave_start_time, wave_end_time, wave_time = get_wave_start_end()

        embed = Embed(title='Current Wave Timer',
                             color=0x1ABC9C)

        embed.add_field(
            name='\u200b',   #\u200b is a zero-width space!
            value=(
                f"⭐ **Start:** <t:{wave_start_time}:t> (<t:{wave_start_time}:R>)\n"
                f"⭐ **End:** <t:{wave_end_time}:t> (<t:{wave_end_time}:R>)"
                "\n"
                "\n"
                f"⭐ **Wave Time When Message Was Sent:** +{wave_time}"),
            inline=False)

        await ctx.message.add_reaction("👋")
        await ctx.send(embed=embed)
        
async def setup(bot):
    await bot.add_cog(Wave(bot))