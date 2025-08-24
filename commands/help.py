############################################################
#Prints this list of abridged help information
#use: 
#   $help
#e.g., '$help' will print a help embed with all commands
############################################################

from discord.ext import commands
from discord import Embed

class Help(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Prints this list of abridged help information.\nExample usage: $help')
    async def help(self, ctx):
        #create embed
        embed = Embed(
            title='F2P Starhunter Help Menu',
            description='Commands List:',
            color=0x1ABC9C
        )
        
        #loop through all bot commands and add help fields
        for command in self.bot.commands:
            if command.help is not None:
                embed.add_field(name=f'${command.name}', value=command.help, inline=False)
        
        #send embed to channel
        await ctx.send(embed=embed)
        

async def setup(bot):
    await bot.add_cog(Help(bot))