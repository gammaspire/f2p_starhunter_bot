############################################################
#print current wave time into the chat!   
#use:
#    $wave
############################################################

from discord.ext import commands
from discord import Embed, app_commands, Interaction
import sys

sys.path.insert(0, '../utils')
from googlesheet_utils import get_wave_start_end

sys.path.insert(0, '../config')
from config import GUILD


class Wave(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    async def _create_embed(self):
        wave_start_time, wave_end_time, wave_time = await get_wave_start_end()

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
        
        return embed
    
    ############################################################
    #prefix command: $wave
    ############################################################
    @commands.command(help='Prints current wave start time, end time, and the wave time at which the message was sent.\nPrefix Command: $wave')
    async def wave(self, ctx):
        
        embed = await self._create_embed()

        await ctx.message.add_reaction("👋")
        await ctx.send(embed=embed)
    
    ############################################################
    #slash command: /wave
    ############################################################
    @app_commands.command(name='wave', description='Prints current wave start time, end time, and the wave time at which the message was sent.')
    async def wave_slash(self, interaction: Interaction):
        
        embed = await self._create_embed()
        await interaction.response.send_message(embed=embed)
        
        #fetch the message object after sending
        sent_msg = await interaction.original_response()
        
        #add the fun little wave emoji
        await sent_msg.add_reaction("👋")
    
#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the Wave.wave_slash method in the class Wave
    #As such, we are accessing the function object directly
#here is the strange part...we are ADDING a decorator to an already existing function
    #treat the decorator as decorator=app_commands.guilds(GUILD)
    #then...app_commands.guilds(GUILD)(Wave.wave_slash) is equivalent to decorator(Wave.wave_slash)
if GUILD is not None:
    Wave.wave_slash = app_commands.guilds(GUILD)(Wave.wave_slash)
        
    
async def setup(bot):
    await bot.add_cog(Wave(bot))