############################################################
#print wave guide URL into the chat!
#use:
#    $guide
############################################################

from discord.ext import commands
from discord import app_commands, Interaction

from config import GUILD

def print_guide():
    return 'Check out out Scouting Guide [Here!](https://docs.google.com/presentation/d/17bU-vGlOuT0MHBZ9HlTrfQEHKT4wHnBrLTV2_HC8LQU/)'


class Guide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    ############################################################
    #prefix command: $guide
    ############################################################
    @commands.command(help='Prints link to our scouting guide, courtesy of WoolyClamoth.\nPrefix Command: $guide')
    async def guide(self, ctx):
        await ctx.send(print_guide())
        
    ############################################################
    #slash command: /guide
    ############################################################    
    @app_commands.command(name='guide',description='Prints the link to our scouting guide.')
    async def guide_slash(self, interaction: Interaction):
        interaction.response.send_message(print_guide())

#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Guide.guide_slash = app_commands.guilds(GUILD)(Guide.guide_slash)           

async def setup(bot):
    await bot.add_cog(Guide(bot))