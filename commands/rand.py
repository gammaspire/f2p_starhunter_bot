################################################
#pulls randomly-generated random fact
#result is JSON, so the json module ensures we can more easily work with the data
################################################

import requests
from discord.ext import commands
import json

def get_random_quote():
    response = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random")
    json_data = json.loads(response.text)   #converts API to JSON (I guess)
    quote = json_data["text"]   #format is from trial and error
    return quote

class Rand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rand(self, ctx):
        quote = get_random_quote()
        await ctx.send(quote)
        
async def setup(bot):
    await bot.add_cog(Rand(bot))