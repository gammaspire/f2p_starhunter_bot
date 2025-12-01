############################################################
#Print random inspirational quote, taken from Dave Tarnowski's "Disappointing Affirmations.
#use: 
#   $inspire
############################################################
import random
from discord.ext import commands
from discord import app_commands, Interaction

from config import GUILD


#load list of affirmations     
def load_affirmations():
    try:
        #note that I am running main.py from the root (parent) directory, so that is where the bot will begin looking
        #for keyword_lists. do NOT assume it is starting in commands/.
        with open("keyword_lists/affirmations.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print('keyword_lists/affirmations.txt file not found; loading default list instead.')
        return ['Keep doing your best.','Just keep swimming.','One moment at a time.',
                'Save those tears for your pillow.','Cheer up, I guess.','Absorb some sunshine.'] 


class Inspire(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ############################################################
    #prefix command: $inspire
    ############################################################
    @commands.command()
    async def inspire(self, ctx):
        affirmations = load_affirmations()
        
        #randomly select 4 affirmations
        random_list = random.choices(affirmations, k=4)
        
        #randomly select and send one affirmation from this list
        await ctx.send(random.choice(random_list))
    
    ############################################################
    #slash command: /inspire
    ############################################################
    @app_commands.command(name='inspire',description='Print an inspirational quote.')
    async def inspire_slash(self, interaction: Interaction):
        affirmations = load_affirmations()
        
        #randomly select 4 affirmations
        random_list = random.choices(affirmations, k=4)
        
        #randomly select and send one affirmation from this list
        await interaction.response.send_message(random.choice(random_list))

#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Inspire.inspire_slash = app_commands.guilds(GUILD)(Inspire.inspire_slash)
        
async def setup(bot):
    await bot.add_cog(Inspire(bot))