############################################################
#print a random joke, courtesy of our own tj44
#use: 
#   e.g., $joke
#   print randomly-generated TJ joke
############################################################

from discord.ext import commands
import random
import os


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

    @commands.command()  #help='Prints a random punny joke, courtesy of OSRS user tj44.\nExample usage: $joke')
    async def joke(self, ctx):
        joke_list = load_tj_jokes()
        chosen_joke = random.choice(joke_list)
        await ctx.send(chosen_joke)
    
    
async def setup(bot):
    await bot.add_cog(Joke(bot))