############################################################
#print list of current backup stars in an aesthetic textbox
#use: 
#   $backups
############################################################  

from discord.ext import commands
from discord import app_commands, Interaction
import sys

sys.path.insert(0, '../utils')
from embed_utils import send_embed

sys.path.insert(0,'../config')
from config import GUILD, RANKED_ROLE_NAME


class Backups(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    ############################################################
    #prefix command: $backups
    ############################################################
    @commands.command(help=f'Prints list of backup worlds. Restricted to @{RANKED_ROLE_NAME} role.\nPrefix Command: $backups')
    @commands.has_role(RANKED_ROLE_NAME)
    async def backups(self, ctx):
        try:
            await send_embed('held_stars.json', ctx, hold=True)
        except Exception as e:
            await ctx.send(f"Error loading backup stars: {e}.")

    ############################################################
    #slash command: /backups
    ############################################################   
    @app_commands.command(name="backups", description=f"Prints list of backup worlds. Restricted to @{RANKED_ROLE_NAME} role.")
    @app_commands.checks.has_role(RANKED_ROLE_NAME)
    async def backups_slash(self, interaction : Interaction):
        try:
            await send_embed('held_stars.json', interaction, hold=True)
        except:
            await interaction.response.send_message(f"Error loading backup stars: {e}.")
    
#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Backups.backups_slash = app_commands.guilds(GUILD)(Backups.backups_slash)       

async def setup(bot):
    await bot.add_cog(Backups(bot))