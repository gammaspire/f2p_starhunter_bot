############################################################
#Hurl a snowball at an unsuspecting user
#use: 
#   /snowball @user
############################################################

import random

from discord import utils
from discord.ext import commands
from discord import app_commands, Interaction, Member

from config import GUILD


def load_snowpile():
    snowpile = 'keyword_lists/snowballs.txt'
    try:
        #note that I am running main.py from the root (parent) directory, so that is where the bot will begin looking
        #for keyword_lists. do NOT assume it is starting in commands/.
        with open(snowpile, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print('keyword_lists/snowballs.txt file not found; loading default list instead.')
        return ['What a silly person', 'I bet you have never touched grass before', 'Absorb some sunshine.'] 


class Snow(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ############################################################
    #slash command: /snowball @user
    ############################################################
    @app_commands.command(name='snowball', description=f'Hurl a snowball at an unsuspecting user.')
    
    async def snowball(self, interaction: Interaction, user: Member):
        
        #generate random integer between 1 and 10. if 9, then the snowball will MISS!
        integer = random.randint(1,10)
        print(integer)
        
        #pull the names of the thrower and targer
        author_id = interaction.user.id
        target_id = user.id
        target_name = str(user.display_name)
        
        if author_id == target_id:
            message = f'-# I will not promote self-degradation, {target_name}.'
        
        elif integer==9:
            message = f'Oh dear, an invincibility shield suddenly surrounds {target_name}! Your snowball harmlessly bounces off of the shell of safety and disintegrates.'
        
        else:
            #choose from the list of insult--I mean snowball--options.
            random_list = random.choices(load_snowpile(), k=4)
            message = random.choice(random_list)
        
        await interaction.response.send_message(f"-# You've been targeted, {user.mention}!\n\n{message}")

        
#attaching a decorator to a function after the class is defined...
if GUILD is not None:
    Snow.snowball = app_commands.guilds(GUILD)(Snow.snowball)   


async def setup(bot):
    await bot.add_cog(Snow(bot))