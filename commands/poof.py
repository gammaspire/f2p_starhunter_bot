############################################################
#manually remove active star from the list
#use: 
#   $poof f2p_world
#e.g., 
#   $poof 308
############################################################        

from discord.ext import commands
from discord import app_commands, Interaction

from scheduler_utils import scheduler
from universal_utils import load_f2p_worlds
from googlesheet_utils import get_wave_time
from star_utils import add_star_to_list, remove_star

from config import GUILD, RANKED_ROLE_NAME


class Poof(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    #shared logic for poofing a star
    #the _ just indicates that this is a helper function to be used only within the class
    async def _poof_logic(self, world, send_func):
        if world is None:
            await send_func('I cannot poof anything if you do not tell me a world.')
            return
        
        if str(world) not in load_f2p_worlds():
            await send_func('All I am asking for is for you to enter a valid F2P world. I beg you.')
            return

        #remove star from .json
        loc, tier = remove_star(world, 'active_stars.json', output_data=True)

        if loc is None:
            current_wave = await get_wave_time()
            await send_func(f'Either an unexpected error has occurred OR there was no active world listed for {world}! The current wave time is +{current_wave}.')
            return

        wave_time = await get_wave_time()
        await send_func(f"⭐ Confirming poof of star \nWorld: {world}\nLoc: {loc}\nTier: {tier}\nThe current wave time is +{wave_time}")

    
    ############################################################
    #prefix command: $poof
    ############################################################
    @commands.command(help=f'Manually removes star from active list, but only if not still active on SM. Restricted to @{RANKED_ROLE_NAME} role.\nPrefix example: $poof 308')
    @commands.has_role(RANKED_ROLE_NAME)
    async def poof(self, ctx, world=None):
        await self._poof_logic(world, ctx.send)


    ############################################################
    #slash command: /poof
    ############################################################
    @app_commands.command(name='poof', description=f'Remove star from the active list, but only if not still active on SM. Restricted to @{RANKED_ROLE_NAME} role.')
    @app_commands.checks.has_role(RANKED_ROLE_NAME)
    
    async def poof_slash(self, interaction: Interaction, world: str):
        #for slash commands, send_func uses interaction.response.send_message
        async def send_func(message):
            await interaction.response.send_message(message)
        
        await self._poof_logic(world, send_func)

#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Poof.poof_slash = app_commands.guilds(GUILD)(Poof.poof_slash)   

async def setup(bot):
    await bot.add_cog(Poof(bot))