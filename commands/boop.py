############################################################
#Prints bot-kun's latency, which is a measure of how long 
#the bot takes to communicate with Discord's servers 
#use: 
#   $boop
#or
#   /boop
############################################################

from discord.ext import commands
from discord import app_commands, Interaction

from config import GUILD


class Boop(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    ############################################################
    #prefix command: $boop
    ############################################################
    @commands.command(name='boop', help='Boop the bot\nPrefix Command: $boop')
    async def boop(self, ctx):
        await ctx.send(f"I've been booped!\nLatency: {round(self.bot.latency*1000)}ms")
    
    ############################################################
    #slash command: /boop
    ############################################################    
    @app_commands.command(name="boop", description="Boop the bot")  
    async def boop_slash(self, interaction: Interaction):
        await interaction.response.send_message(f"I've been booped!\nLatency: {round(self.bot.latency*1000)}ms")

#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Boop.boop_slash = app_commands.guilds(GUILD)(Boop.boop_slash)           

    
async def setup(bot):
    
    #add the Boop cog
    await bot.add_cog(Boop(bot))