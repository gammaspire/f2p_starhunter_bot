############################################################
#print a random joke, courtesy of our own tj44
#use: 
#   e.g., $joke
#   print randomly-generated TJ joke
############################################################

from discord.ext import commands
from discord import app_commands, Interaction
import random
import os

from config import GUILD

#load TJ jokes from file; fallback to default jokes if file not found
def load_tj_jokes():
    path = os.path.join("keyword_lists", "tj_jokes.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            tj_jokes = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{path} file not found; loading default list instead.")
        tj_jokes = [
            "Did you hear about the bacon that got sick? It was later cured!",
            "Do you know the song 'acne'? It was a breakout hit."
        ]
    return tj_jokes

    
class Joke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ############################################################
    #prefix command: $joke
    ############################################################
    @commands.command()  #help='Prints a random punny joke, courtesy of OSRS user tj44.\nExample usage: $joke')
    async def joke(self, ctx):
        joke_list = load_tj_jokes()
        chosen_joke = random.choice(joke_list)
        await ctx.send(chosen_joke)
    
    ############################################################
    #slash command: /joke
    ############################################################
    @app_commands.command(name='joke', description='Print a punny joke, courtesy of OSRS user tj44.')
    async def joke_slash(self, interaction: Interaction):
        joke_list = load_tj_jokes()
        chosen_joke = random.choice(joke_list)
        await interaction.response.send_message(chosen_joke)
    
#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Joke.joke_slash = app_commands.guilds(GUILD)(Joke.joke_slash)   
    
async def setup(bot):
    await bot.add_cog(Joke(bot))