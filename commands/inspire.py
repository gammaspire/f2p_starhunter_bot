############################################################
#Print random inspirational quote, taken from Dave Tarnowski's "Disappointing Affirmations.
#use: 
#   $inspire
############################################################
import random
from discord.ext import commands


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

    @commands.command()
    async def inspire(self, ctx):
        affirmations = load_affirmations()
        await ctx.send(random.choice(affirmations))
        
async def setup(bot):
    await bot.add_cog(Inspire(bot))