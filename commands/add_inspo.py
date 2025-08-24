############################################################
#add encouragements to the 'grab bag' list, only if phrase is unique and not already in the list
#use: 
#   $add_inspo encouraging_phrase_here
############################################################

from discord.ext import commands
import sys
import os

sys.path.insert(0,'../utils')
from recreation_utils import load_encouragement_keywords


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
            
async def setup(bot):
    await bot.add_cog(Add_Inspo(bot))