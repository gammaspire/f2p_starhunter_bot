############################################################
#Print the key to our shorthand for star spawning locations!
#use: 
#   $loc shorthand
#e.g., '$loc nc' will output 'North Crandor'
############################################################

from discord.ext import commands
from discord import app_commands, Interaction

from star_utils import load_loc_dict

from config import GUILD


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
        
    ############################################################
    #prefix command: $loc
    ############################################################
    @commands.command(help='Prints the full location corresponding to our scouting loc shorthand.\n'
                           'Prefix example: $loc apa')
    async def loc(self, ctx, shorthand):
        loc_shorthand, loc_key = print_loc_key(shorthand)
        await ctx.send(f'{loc_shorthand} = {loc_key}\n\n'
                       f'See https://locations.dust.wiki for a list of our scouting shorthand and the full map of exact F2P spawn locations!')    
        
    ############################################################
    #slash command: /loc
    ############################################################
    @app_commands.command(name='loc', description='Prints the full location corresponding to our scouting loc shorthand.')
    async def loc_slash(self, interaction: Interaction, shorthand: str):
        loc_shorthand, loc_key = print_loc_key(short)
        await interaction.message.send_response(f'{loc_shorthand} = {loc_key}\n\n'
                                                f'See https://locations.dust.wiki for a list of our scouting shorthand and the full map of exact F2P spawn locations!')  

        
#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Loc.loc_slash = app_commands.guilds(GUILD)(Loc.loc_slash)   


async def setup(bot):
    await bot.add_cog(Loc(bot))