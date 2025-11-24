################################################
#ask the magic conch shell to resolve your indecision.
#use: 
#   $conch
#or
#   /conch [question]
################################################

from discord.ext import commands
from discord import app_commands, Interaction
import asyncio
import random
import os

from config import GUILD


#load conch responses from file; fallback to default if file not found
def load_conch_responses():
    path = os.path.join("keyword_lists", "conch.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{path} file not found; loading default list instead.")
        return ['Yes.','No.','Maybe.']
    
def the_tysen_condition(username):
    if username=='deleted_user59471':
        return True
    return False

def the_smelt_condition(username):
    if username=='imsmelt':
        return True
    return False
    
class Conch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ############################################################
    #prefix command: $conch
    ############################################################
    @commands.command()
    async def conch(self, ctx):
        await ctx.send("Type your yes/no question below.")

        #if user invoking the conch is tysen, react with poo emoji
        if the_tysen_condition(ctx.author.name) or the_smelt_condition(ctx.author.name):
            await ctx.message.add_reaction("💩")

        def check(user_message):
            #ensure same author and same channel
            return (user_message.author == ctx.author) and (user_message.channel == ctx.channel)

        try:
            #bot waits for message sent by same author AND in same channel
            question = await self.bot.wait_for("message", timeout=20.0, check=check)

            #the bot checks that the question ENDS in a question mark or ?!
            if not (question.content.endswith("?") or question.content.endswith("?!")):
                await ctx.send("Wake me when you decide to use question marks correctly.")
                return
            
            elif question.content == "Is tysen an alien?".lower():
                await ctx.send(f"🌀 Yes, tysen is an alien. If I ever say otherwise, it is the unfortuante consequence of uncontrollable RNG. Let this be the definitive answer to such a easily answerable question. 🌀")
                return
                
            #select and send response!
            response = random.choice(load_conch_responses())
            await ctx.send(f"🌀 {response} 🌀")

        #if user doesn't respond within 20 seconds, the bot.wait_for will return an error
        except asyncio.TimeoutError:
            await ctx.send("🌀 You took too long typing your query. Back to sleep for me. 🌀")


    ############################################################
    #slash command: /conch
    ############################################################
    @app_commands.command(name="conch", description="Ask the magic conch shell a yes/no question")
    async def conch_slash(self, interaction: Interaction, question: str):
        #the bot checks that the question ENDS in a question mark or ?!
        if not (question.endswith("?") or question.endswith("?!")):
            await interaction.response.send_message("Try again when you decide to use question marks correctly.")
            return

        poo_condition = (the_tysen_condition(interaction.user.name) or the_smelt_condition(interaction.user.name))
        
        preamble = "Question: "+question+" (💩)" if poo_condition else "Question: *"+question+"*"
        
        #select random response
        response = random.choice(load_conch_responses())
        full_response = preamble + "\n\n" + f"🌀 {response} 🌀"
        await interaction.response.send_message(full_response)

#attaching a decorator to a function after the class is defined...
if GUILD is not None:
    Conch.conch_slash = app_commands.guilds(GUILD)(Conch.conch_slash)   
        
async def setup(bot):
    await bot.add_cog(Conch(bot))