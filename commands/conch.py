################################################
#ask the magic conch shell to resolve your indecision.
#use: 
#   $conch
################################################

from discord.ext import commands
import asyncio
import random
import os


#load conch responses from file; fallback to default if file not found
def load_conch_responses():
    path = os.path.join("keyword_lists", "conch.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{path} file not found; loading default list instead.")
        return ['Yes.','No.','Maybe.']
    

class Conch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def conch(self, ctx):
        await ctx.send("Type your yes/no question below.")
    
        #if user invoking the conch is tysen, react with poo emoji
        if ctx.author.name=='deleted_user102727':
            await ctx.message.add_reaction("💩")

        def check(user_message):
            #ensure same author and same channel
            return (user_message.author == ctx.author) and (user_message.channel == ctx.channel)

        try:
            #bot waits for message sent by same author AND in same channel
            question = await self.bot.wait_for("message", timeout=20.0, check=check)

            #the bot checks that the question ENDS in a question mark or ?!
            if not (question.content.endswith("?") or question.content.endswith("?!")):
                await ctx.send("Your grammar is abysmal. Wake me when you decide to use question marks correctly.")
                return

            #select and send response!
            response = random.choice(load_conch_responses())
            await ctx.send(f"🌀 {response} 🌀")

        #if user doesn't respond within 20 seconds, the bot.wait_for will return an error
        except asyncio.TimeoutError:
            await ctx.send("🌀 You took too long typing your query. The conch has gone back to sleep. 🌀")
            

async def setup(bot):
    await bot.add_cog(Conch(bot))