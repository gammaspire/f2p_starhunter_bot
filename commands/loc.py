############################################################
#Print the key to our shorthand for star spawning locations!
#use: 
#   $loc shorthand
#e.g., '$loc nc' will output 'North Crandor'
############################################################

from discord.ext import commands
import sys

sys.path.insert(0, '../utils')

from star_utils import load_loc_dict


def print_loc_key(loc_shorthand):
    try:
        loc_dict = load_loc_dict()
    except:
        print('Oh no! keyword_lists/locs.txt not found or corrupted!')
        return None, 'Error loading location dictionary.'
    
    try:
        return loc_shorthand, loc_dict[loc_shorthand]
    except KeyError:
        return loc_shorthand, 'Location invalid!'


class Loc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(
        help='Prints the full location corresponding to our scouting loc shorthand.\n'
             'Example usage: $loc apa')
    
    async def loc(self, ctx, shorthand):
        loc_shorthand, loc_key = print_loc_key(shorthand)
        await ctx.send(
            f'{loc_shorthand} = {loc_key}\n\n'
            f'See https://locations.dust.wiki for a list of our scouting shorthand and the full map of exact F2P spawn locations!')    
        

async def setup(bot):
    await bot.add_cog(Loc(bot))