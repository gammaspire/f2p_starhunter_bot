############################################################
#print list of current active stars in an aesthetic textbox
#use: 
#   $active
############################################################     

from discord.ext import commands
from discord import Interaction, app_commands
import sys

sys.path.insert(0, '../utils')
from embed_utils import send_embed

sys.path.insert(0,'../config')
from config import GUILD


class Active(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    ############################################################
    #prefix command: $active
    ############################################################
    @commands.command(help='Prints list of active stars.\nPrefix Command: $active')
    async def active(self, ctx):
        await send_embed('active_stars.json', ctx, active=True)
    
    ############################################################
    #slash command: /active
    ############################################################ 
    @app_commands.command(name="active", description="Prints list of active stars")  
    @app_commands.guilds(GUILD)  #optional: restrict to testing guild for instant visibility
    async def active_slash(self, interaction: Interaction):
        await send_embed('active_stars.json', interaction, active=True)

#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Active.active_slash = app_commands.guilds(GUILD)(Active.active_slash)   
        
async def setup(bot):
    await bot.add_cog(Active(bot))