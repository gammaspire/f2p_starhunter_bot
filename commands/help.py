############################################################
# Prints this list of abridged help information
# Use:
#   $help
# or
#   /help
############################################################

from discord.ext import commands
from discord import Embed, app_commands, Interaction

#import TEST_GUILD_ID for testing
import sys
sys.path.insert(0,'../config')
from config import GUILD

class Help(commands.Cog):
    """
    Cog that implements both prefix and slash command variants
    for displaying a help menu with all bot commands.
    """
    
    def __init__(self, bot):
        self.bot = bot

    ############################################################
    # Prefix command: $help
    ############################################################
    @commands.command(help='Prints this list of abridged command help.\n'
                           'Prefix Command: $help\n'
                           'Slash Command: /help')
    async def help(self, ctx):
        """
        Sends an embed listing all bot commands and their descriptions.
        """
        embed = Embed(
            title='F2P Starhunter Help Menu',
            description='Commands List:',
            color=0x1ABC9C)
        
        #loop through all bot commands and add help fields
        for command in self.bot.commands:
            if command.help is not None:
                embed.add_field(name=f'${command.name} | /{command.name}', value=command.help, inline=False)
        
        #send embed as ephemeral response so others cannot see it
        await ctx.send(embed=embed, ephemeral=True)

    ############################################################
    # Slash command variant: /help
    ############################################################
    @app_commands.command(name="help", description="Prints list of abridged command help.")
    async def help_slash(self, interaction: Interaction):
        """
        Sends an ephemeral embed listing all bot commands and their descriptions
        when the /help slash command is invoked.
        """
        embed = Embed(
            title='F2P Starhunter Help Menu',
            description='Commands List:',
            color=0x1ABC9C)
        
        for command in self.bot.commands:
            if command.help is not None:
                embed.add_field(name=f'${command.name}', value=command.help, inline=False)
        
        #send embed as ephemeral response so others cannot see it
        await interaction.response.send_message(embed=embed, ephemeral=True)

#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Help.help_slash = app_commands.guilds(GUILD)(Help.help_slash)   
        
############################################################
# Cog setup function
############################################################
async def setup(bot):
    """
    Adds the Cog to the bot and registers the slash command with the bot's tree.
    Slash command syncing is handled centrally in main.py's on_ready().
    """
    cog = Help(bot)
    await bot.add_cog(cog)

    #register the slash command with the bot's command tree
    #as of Discord 2.5x, @app.commands.command automatically registers slash commands.
    #all I need to do is sync the tree!
    #bot.tree.add_command(cog.help_slash, guild=guild)
    #await bot.tree.sync(guild=guild)

