############################################################
#Event listener for messages to trigger encouragements
#the activates when something happens (in this case, when the bot receives message)
############################################################

from discord.ext import commands
import random

from recreation_utils import load_sad_keywords, load_encouragement_keywords, sarcastify_word


class Encouragements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    #the function is called when something happens (in this case, when the bot receives message)
    async def on_message(self, message):
        
        #if the message is from the bot, the bot will not respond...and this function will "exit"
        if message.author == self.bot.user:
            return
        
        #MOREOVER, if the 1-10 RNG rolls any number but 5, ignore.
        if random.randint(1,10) != 5:
            return
        
        #grab display name (name) and username of the message author
        name = message.author.display_name
        username = message.author.name
        
        ############################################################
        #If message includes any of the keywords, random encouraging message will print
        #use: 
        #   e.g., user types "I am feeling upset"
        #   bot might respond with "Absorb some sunshine."
        ############################################################
        sad_keywords = set(load_sad_keywords())
        
        if any(word in message.content for word in sad_keywords):
            encouragement = load_encouragement_keywords()
            chosen_encouragement = random.choice(encouragement)
            
            #there is a secret response prompt -- "sarcasm"
            #in this case, find the (or a) sad word in the user's message and *sArCaStiFy iT*
            if chosen_encouragement == 'sarcasm':
                
                #quickest approach computationally to finding the sad word is to convert both lists to a set, 
                #then find the sad word that triggered this function
                try:
                    word = list(set(message.content.split()).intersection(sad_keywords))[0]
                except:
                    word = 'unhappy'
                
                chosen_encouragement = sarcastify_word(word)
            
            await message.channel.send(chosen_encouragement)
            
            #IMPORTANT: no need to call process_commands here.
            #commands will still work normally after this listener runs.
            return


async def setup(bot):
    await bot.add_cog(Encouragements(bot))