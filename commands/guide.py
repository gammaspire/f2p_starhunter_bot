############################################################
#print wave guide URL into the chat!
#use:
#    $guide
############################################################

from discord.ext import commands

def print_guide():
    return 'Check out out Scouting Guide [Here!](https://docs.google.com/presentation/d/17bU-vGlOuT0MHBZ9HlTrfQEHKT4wHnBrLTV2_HC8LQU/)'


class Guide(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(help='Prints link to our scouting guide, courtesy of WoolyClamoth.\nExample usage: $guide')
    async def guide(self, ctx):
        await ctx.send(print_guide())
    

async def setup(bot):
    await bot.add_cog(Guide(bot))