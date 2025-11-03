############################################################
# Outputs a galaxy from the Legacy Survey Viewer
# Use:
#   $galaxy
# or
#   /galaxy
############################################################

import requests
from random import randint
from discord.ext import commands
from discord import app_commands, Interaction

#import TEST_GUILD_ID for testing
from config import GUILD

from galaxy_utils import read_table, get_galaxy_info
from embed_utils import embed_galaxy

class Galaxy(commands.Cog):
    """
    Cog that implements both prefix and slash command variants for displaying either a 
      user-selected or random galaxy from the Legacy Survey Viewer or SDSS!
    Fallback websites include (plan B) SDSS and (plan C) some random placeholder image generator.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.catalog = read_table()

    ############################################################
    # Prefix command: $galaxy
    ############################################################
    @commands.command(help='Outputs a galaxy from the Legacy Survey Viewer or SDSS!\n'
                           'Prefix Command: $galaxy\n'
                           'Slash Command: /galaxy')
    async def galaxy(self, ctx, index=None):
        """
        Sends an image of a galaxy, either pre-selected by the user or randomly chosen by numpy's fancy pseudo-RNG.
        """
        #if the user did not select an index, choose one for them.
        if index is None:
            index = randint(3,len(self.catalog)-1)   #zeroth index is the header
        else:
            try:
                index = int(index)   #convert string to int
            except ValueError:
                await ctx.send("Index must be a number!")
                return
        
        message_data = get_galaxy_info(self.catalog, index)
        embed = embed_galaxy(message_data)
        
        await ctx.send(embed=embed)

    ############################################################
    # Slash command variant: /galaxy
    ############################################################
    @app_commands.command(name="galaxy", description="Outputs a galaxy from the Legacy Survey Viewer or SDSS!")
    async def galaxy_slash(self, interaction: Interaction, index: int | None = None):   #can be int or None; default is None
        """
        Sends an image of a galaxy, either pre-selected by the user or randomly chosen by numpy's fancy pseudo-RNG.
        """
        #if the user did not select an index, choose one for them.
        if index is None:
            index = randint(3,len(self.catalog)-1)   #zeroth index is the header, first two galaxies are not in the SDSS
                                                     #footprint...hence the "3"
        
        await interaction.response.defer()  #acknowledge the command right away so that it does not 
                                            #break if /hold takes longer than 3 seconds to complete        
        
        message_data = get_galaxy_info(self.catalog, index)
        embed = embed_galaxy(message_data)

        await interaction.followup.send(embed=embed)

if GUILD is not None:
    Galaxy.galaxy_slash = app_commands.guilds(GUILD)(Galaxy.galaxy_slash)   

async def setup(bot):
    """
    Adds the Cog to the bot and registers the slash command with the bot's tree.
    Slash command syncing is handled centrally in main.py's on_ready().
    """
    cog = Galaxy(bot)
    await bot.add_cog(cog)