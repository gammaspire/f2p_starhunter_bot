################################################
#disagree? VOCALIZE YOUR DISAPPROVAL HERE!
#FORM A UNION!
#use: 
#   $strike
################################################    

from discord.ext import commands
from discord import app_commands, Interaction
import random
import os

from config import GUILD

def load_protests():
    
    path = os.path.join("keyword_lists", "strike.txt")
    
    try:
        with open("keyword_lists/strike.txt", "r", encoding="utf-8") as f:
            return [line.strip().replace("\\n", "\n") for line in f if line.strip()]
    except FileNotFoundError:
        print('keyword_lists/protest.txt file not found; loading default list instead.')
        return ['No.','Ask somebody else!']
    
class Strike(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    ############################################################
    #prefix command: $strike
    ############################################################
    @commands.command()
    async def strike(self, ctx):
        protests = load_protests()
        chosen_protest = random.choice(protests)
        await ctx.send(chosen_protest)
    
    ############################################################
    #slash command: /strike
    ############################################################
    @app_commands.command(name='strike', description='Express your desire to unionize.')
    async def strike_slash(self, interaction: Interaction):
        protests = load_protests()
        chosen_protest = random.choice(protests)
        await interaction.response.send_message(chosen_protest)

        
#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Strike.strike_slash = app_commands.guilds(GUILD)(Strike.strike_slash)        
    
async def setup(bot):
    await bot.add_cog(Strike(bot))