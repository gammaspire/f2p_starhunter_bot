############################################################
#Print list of worlds in order from early- to late-wave spawns
#Will remove any worlds currently harboring stars, per $active
#Outputs comma-separated list to paste into Runelite plugin
#use: 
#   $hoplist
############################################################  

from discord.ext import commands
from discord import app_commands, Interaction

from hoplist_utils import send_hoplist_message

from config import GUILD

from refresh_button import RefreshView


class Hoplist(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    ############################################################
    #prefix command: $hoplist
    ############################################################
    @commands.command(
        help='Prints comma-separated world list in order of early- to late-wave spawns. '
             'Filters out $active worlds.\nPrefix Command: $hoplist')
    async def hoplist(self, ctx):
        #sends the hoplist using the utility function, which handles formatting
        #'None' for message_id will make the function send a fresh message
        try:
            view = RefreshView()
            message = await send_hoplist_message(ctx.channel, None, refresh_count=view.refresh_count)
            await message.edit(view=view)   # attach refresh button to same message
            view.message = message          # link the view to its message
        except Exception as e:
            print(e)
        #ezpz!
        
    ############################################################
    #slash command: /hoplist
    ############################################################
    @app_commands.command(name='hoplist', description='Prints comma-separated, filtered world list in order of early- to late-wave spawns.')
    async def hoplist_slash(self, interaction: Interaction):
        try:
            view = RefreshView()
            message = await send_hoplist_message(channel=interaction.channel, message_id=None, interaction=interaction,
                                                refresh_count=view.refresh_count)
            await message.edit(view=view)   # attach refresh button
            view.message = message
        except Exception as e:
            print(e)

#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Hoplist.hoplist_slash = app_commands.guilds(GUILD)(Hoplist.hoplist_slash)   
    
async def setup(bot):
    await bot.add_cog(Hoplist(bot))