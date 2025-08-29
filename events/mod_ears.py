from discord.ext import commands
from discord import app_commands, Interaction

#listen for permission errors!
class CommandErrorFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        #register the slash command error handler -- NEEDED!
        bot.tree.error(self.on_app_command_error)

    #helper function for permission error responses
    #only to be used within the class...hence the _ prefix naming convention
    async def _handle_permission_error(self, user, command_name, responder):
        """Centralized handler for permission errors."""
        print(f'{user} tried to use {command_name}. Oops.')
        await responder("Oops, you don’t have permission to use that command!")

    #prefix commands -- if permission error occurs with prefix command, this error occurs.
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            await self._handle_permission_error(
                f"{ctx.author.name} ({ctx.author.display_name})",
                f"${ctx.command}",  ctx.send)

    #slash commands -- if permission error occurs with slash command, this error occurs
    async def on_app_command_error(self, interaction: Interaction, error: app_commands.AppCommandError):
        if isinstance(error, (app_commands.MissingRole, app_commands.MissingAnyRole)):
            async def responder(msg):
                if not interaction.response.is_done():
                    await interaction.response.send_message(msg, ephemeral=True)
                else:
                    await interaction.followup.send(msg, ephemeral=True)

            await self._handle_permission_error(
                f"{interaction.user.name} ({interaction.user.display_name})",
                f"/{interaction.command.name}",
                responder)

async def setup(bot):
    await bot.add_cog(CommandErrorFilter(bot))