############################################################
#manually remove backup star from the list
#(doing so will also remove the scheduled 'ping' to call)
#use: 
#   $remove f2p_world
#e.g., 
#   $remove 308
############################################################  

from discord.ext import commands
from discord import app_commands, Interaction
import sys

sys.path.insert(0, '../utils')
from scheduler_utils import scheduler
from universal_utils import load_f2p_worlds
from star_utils import remove_star

sys.path.insert(0, '../config')
from config import GUILD

class Remove(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    ############################################################
    #prefix command: $remove
    ############################################################
    @commands.command(help='Manually removes star from backups list. Restricted to @Ranked role.\nPrefix example: $remove 308')
    @commands.has_role('Ranked')
    async def remove(self, ctx, world=None):

        if (world is None) or (world not in load_f2p_worlds()):
            await ctx.send('Did you forget to use a valid F2P world? I suspected as much. Try again.')
            return

        #remove star from .json
        output = remove_star(world, 'held_stars.json', output_data=True)

        if output == (None, None):
            await ctx.send(f"World {world} not found in backups list.")
            return

        loc, tier = output
        job_id = f"hold_{world}_{tier}"

        #cancel job, if it exists
        try:
            scheduler.remove_job(job_id)
        except Exception as e:
            print(f"[Warning] Could not remove job '{job_id}': {e}")

        await ctx.send(f"⭐ Removing the following star from backups list:\nWorld: {world}\nLoc: {loc}\nTier: {tier}")

    ############################################################
    #slash command: /remove
    ############################################################
    @app_commands.command(name='remove', description='Manually removes star from backups list. Restricted to @Ranked role.')
    async def remove_slash(self, interaction: Interaction, world: str):
        if (world is None) or (world not in load_f2p_worlds()):
            await interaction.response.send_message('Did you forget to use a valid F2P world? I suspected as much. Try again.')
            return

        #remove star from .json
        output = remove_star(world, 'held_stars.json', output_data=True)

        if output == (None, None):
            await interaction.response.send_message(f"World {world} not found in backups list.")
            return

        loc, tier = output
        job_id = f"hold_{world}_{tier}"

        #cancel job, if it exists
        try:
            scheduler.remove_job(job_id)
        except Exception as e:
            print(f"[Warning] Could not remove job '{job_id}': {e}")

        await interaction.response.send_message(f"⭐ Removing the following star from backups list:\nWorld: {world}\nLoc: {loc}\nTier: {tier}")

#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Remove.remove_slash = app_commands.guilds(GUILD)(Remove.remove_slash)    

async def setup(bot):
    await bot.add_cog(Remove(bot))