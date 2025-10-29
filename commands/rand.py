################################################
#pulls randomly-generated random fact
#result is JSON, so the json module ensures we can more easily work with the data
################################################

import requests
from discord.ext import commands
from discord import app_commands, Interaction
import json

from config import GUILD

#fetch a random quote from the API
def get_random_quote():
    response = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random")
    json_data = json.loads(response.text)   #converts API response to JSON
    quote = json_data["text"]   #extract the fact text
    return quote

class Rand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ################################################
    #prefix command: $rand
    ################################################
    @commands.command()
    async def rand(self, ctx):
        quote = get_random_quote()
        await ctx.send(quote)

    ################################################
    #slash command: /rand
    ################################################
    @app_commands.command(name='rand', description='Returns a randomly generated fact.')
    async def rand_slash(self, interaction: Interaction):
        quote = get_random_quote()
        await interaction.response.send_message(quote)

#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Rand.rand_slash = app_commands.guilds(GUILD)(Rand.rand_slash)   
    
async def setup(bot):
    await bot.add_cog(Rand(bot))