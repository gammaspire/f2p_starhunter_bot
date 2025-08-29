############################################################
#lost_worlds command which prints any inactive f2p worlds which still appear on dust.wiki
#use: 
#   $lost_worlds
############################################################  

from discord.ext import commands
from discord import app_commands, Interaction
import sys

sys.path.insert(0, '../utils')
from universal_utils import load_f2p_worlds

sys.path.insert(0, '../config')
from config import GUILD

class Lost_Worlds(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
     
    ############################################################
    #prefix command: $lost_worlds
    ############################################################
    @commands.command(help='Prints the list of dust.wiki worlds which are not on the currently active OSRS F2P worlds list.\nPrefix Command: $lost_worlds')
    async def lost_worlds(self, ctx):
        try:
            _, omitted_worlds = load_f2p_worlds(output_omitted_worlds=True)
            await ctx.send(f'Here is a list of currently inactive F2P worlds:\n {omitted_worlds}')

        except:
            await ctx.send('Error pulling currently inactive F2P worlds. I guess you will have to use your eyeballs.')
     
    ############################################################
    #slash command: /lost_worlds
    ############################################################
    @app_commands.command(name='lost_worlds', description='Prints list of dust.wiki worlds not currently active OSRS F2P worlds.')
    async def lost_worlds_slash(self, interaction: Interaction):
        try:
            _, omitted_worlds = load_f2p_worlds(output_omitted_worlds=True)
            await interaction.response.send_message(f'Here is a list of currently inactive F2P worlds:\n {omitted_worlds}')
        except:
            await interaction.response.send_message('Error pulling currently inactive F2P worlds. I guess you will have to use your eyeballs.')
    
#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Lost_Worlds.lost_worlds_slash = app_commands.guilds(GUILD)(Lost_Worlds.lost_worlds_slash)       
    
async def setup(bot):
    await bot.add_cog(Lost_Worlds(bot))