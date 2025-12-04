############################################################
#Toss a snowcone to an unsuspecting user
#use: 
#   /snowcone @user
############################################################

import random

from discord import utils
from discord.ext import commands
from discord import app_commands, Interaction, Member

from config import GUILD


def load_icebar():
    icebar = 'keyword_lists/snowcones.txt'
    try:
        #note that I am running main.py from the root (parent) directory, so that is where the bot will begin looking
        #for keyword_lists. do NOT assume it is starting in commands/.
        with open(icebar, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print('keyword_lists/snowcones.txt file not found; loading default list instead.')
        return ['What a cool person.', 'I bet you have touched grass before.', 'You are the sunshine.'] 


class Ice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ############################################################
    #slash command: /snowcone @user
    ############################################################
    @app_commands.command(name='snowcone', description=f'Pass a compliment snowcone to an unsuspecting user.')
    
    async def snowcone(self, interaction: Interaction, user: Member):
        
        try:
            #pull the names of the tosser and targer
            author_id = interaction.user.id
            target_id = user.id
            target_name = str(user.display_name)

            if author_id == target_id:
                message_comp = f"-# {target_name} is administering some self-love! We are proud of you, {target_name}."

            else:
                message_comp=f"-# You've been selected, {user.mention}!"
                
            #choose from the list of snowcone options.
            random_list = random.choices(load_icebar(), k=4)
            message = random.choice(random_list)

            await interaction.response.send_message(message_comp+"\n\n"+message)
        
        except Exception as e:
            print(e)

        
#attaching a decorator to a function after the class is defined...
if GUILD is not None:
    Ice.snowcone = app_commands.guilds(GUILD)(Ice.snowcone)   


async def setup(bot):
    await bot.add_cog(Ice(bot))