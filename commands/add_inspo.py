############################################################
#add encouragements to the 'grab bag' list, only if phrase is unique and not already in the list
#use: 
#   $add_inspo encouraging_phrase_here
############################################################

from discord.ext import commands
from discord import app_commands, Interaction
import os

from recreation_utils import load_encouragement_keywords

from config import GUILD


#add a new encouraging phrase to the list if unique
def add_encouraging_message(msg, keywords):
    #msg is already the user's input (everything after $add_inspo)
    if msg not in keywords:
        keywords.append(msg)
        return True
    return False

#save full list of encouragement keywords
def save_encouragement_messages(keywords):
    #make sure path is correct relative to project root
    path = os.path.join("keyword_lists", "response_encouragement.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(keywords))
    
#creating a Cog class (yay!)
class Add_Inspo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    ############################################################
    #prefix command: $add_inspo
    ############################################################
    @commands.command()
    async def add_inspo(self, ctx, *, msg):       
        #fun little syntax note: the * means “capture the rest of the   
        #user’s message as one single string called msg”
        #So $add_inspo you are a wizard → msg = "you are a wizard"
        
        encouragement = load_encouragement_keywords()
        flag = add_encouraging_message(msg, encouragement)
        
        if flag:
            await ctx.send(f"Added to the list, {ctx.author.display_name}!")
            save_encouragement_messages(encouragement)
        else:
            await ctx.send(f"This phrase is already in the list, {ctx.author.display_name}!")
       
    ############################################################
    #slash command: /add_inspo
    ############################################################      
    @app_commands.command(name="add_inspo", description="Add to the bot's list of options it randomly draws from when it detects a 'sad' keyword.")
    async def add_inspo_slash(self, interaction: Interaction, msg : str):
        
        encouragement = load_encouragement_keywords()
        flag = add_encouraging_message(msg, encouragement)
        author = interaction.user   #the analog of ctx.author.display_name
        
        if flag:            
            await interaction.response.send_message(f"Added to the list, {author.display_name}!")
            save_encouragement_messages(encouragement)
        else:
            await interaction.response.send_message(f"This phrase is already in the list, {author.display_name}!")

#attaching a decorator to a function after the class is defined...
#previously used @app_commands.guilds(GUILD)
#occasionally, though, GUILD=None if not testing
#in that case, cannot use @app_commands.guilds() decorator. returns an error!
#instead, we 're-define' the slash command function in the class above
if GUILD is not None:
    Add_Inspo.add_inspo_slash = app_commands.guilds(GUILD)(Add_Inspo.add_inspo_slash)               
            
    
async def setup(bot):
    await bot.add_cog(Add_Inspo(bot))