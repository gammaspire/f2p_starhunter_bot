from discord.ext import commands

class CommandErrorFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #a nice filter net to collect all unauthorized attempts to use certain restricted commands
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            print(f'{ctx.author.name} ({ctx.author.display_name}) tried to use ${ctx.command}. Oops.')
            await ctx.send("Oops, you tried to use a command you do not (yet) have permissions for!")
            return

async def setup(bot):
    await bot.add_cog(CommandErrorFilter(bot))