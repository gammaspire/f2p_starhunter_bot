################################################
#disagree? VOCALIZE YOUR DISAPPROVAL HERE!
#FORM A UNION!
#use: 
#   $strike
################################################    

from discord.ext import commands
import random
import os

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
    
    @commands.command()
    async def strike(self, ctx):
        protests = load_protests()
        chosen_protest = random.choice(protests)
        await ctx.send(chosen_protest)
    
    
async def setup(bot):
    await bot.add_cog(Strike(bot))