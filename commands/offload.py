############################################################
#Tell the bot to ping a different user for your backup stars!
#use: 
#   /offload @user
############################################################

from discord import utils
from discord.ext import commands
from discord import app_commands, Interaction, Member
import sys

sys.path.insert(0, '../utils')
from universal_utils import load_json_file, save_json_file

sys.path.insert(0, '../config')
from config import GUILD, RANKED_ROLE_NAME

#path to backup stars...
BACKUPS_FILE = 'keyword_lists/held_stars.json'


# "_object" implies that you must input a DISCORD object!
def check_role(bot, author_object, user_object):
    guild_object = author_object.guild
    if guild_object is None:
        return False, "-# Error: Could not find the guild in bot cache."

    ranked_role = utils.get(guild_object.roles, name=RANKED_ROLE_NAME)
    if ranked_role is None:
        return False, f"-# Error: Could not find the {RANKED_ROLE_NAME} role in this server."

    if not hasattr(author_object, "roles") or not hasattr(user_object, "roles"):
        return False, "-# Error: Failed to fetch user role data. Try again in a few seconds."

    if ranked_role not in author_object.roles:
        return False, f"-# You must have the {RANKED_ROLE_NAME} role to offload your stars."

    if ranked_role not in user_object.roles:
        return False, f"-# {user_object.mention} does not have the {RANKED_ROLE_NAME} role and cannot receive offloaded stars."

    return True, None


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ############################################################
    #slash command: /offload @user
    ############################################################
    @app_commands.command(name='offload', description=f'Pings a rankeduser of your choice for your backup stars. Restricted to @{RANKED_ROLE_NAME} role.')
    
    async def ping_slash(self, interaction: Interaction, user: Member):
        
        try:
            #define author and 'target' IDs
            author_id = interaction.user.id
            target_id = user.id
            target_name = str(user.display_name)

            backups = load_json_file(BACKUPS_FILE)
                        
            #check if the target user is worthy!
            role_flag, message = check_role(self.bot, interaction.user, user)
            if not role_flag:
                await interaction.response.send_message(message, ephemeral=True)
                return

            count = 0 #initiate the count

            #look through all of the backup stars. for every instance where the user_id is the author_id,
            #switch both the user_id and the username to the "target" user info
            for entry in backups:
                if entry.get("user_id") == author_id:
                    entry["user_id"] = target_id
                    entry["username"] = target_name
                    count += 1

            #if the author has no backup stars, you know what to do
            if count == 0:
                await interaction.response.send_message(f"Wow, nice try! 'Tis a pity that you do not have backup "
                               "stars to reassign.", ephemeral=True)
                return
                        
            #save the modified .json file!
            save_json_file(backups, BACKUPS_FILE)

            await interaction.response.send_message(f'Your held stars are now the ~~problem~~ responsibility of {user.mention}!')
        except Exception as e:
            print(e)

        
#attaching a decorator to a function after the class is defined...
if GUILD is not None:
    Ping.ping_slash = app_commands.guilds(GUILD)(Ping.ping_slash)   


async def setup(bot):
    await bot.add_cog(Ping(bot))