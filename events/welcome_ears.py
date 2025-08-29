############################################################
#prepares the "welcome" message (either DM or a ping in #general)
#that is sent when a new user joins the server!
############################################################

import os
import discord
from discord.ext import commands

import sys
sys.path.insert(0, '../config')
from config import WELCOME_GUILD, WELCOME_CHANNEL

def prep_welcome_message(new_member):
    
    print('IF YOU ARE TESTING THE WELCOME MESSAGE, MAKE SURE TO EDIT "STARHUNT_GUILD_ID" AND "STARHUNT_CHANNEL_ID" TO "TEST_GUILD_ID" AND "TEST_CHANNEL_ID", RESPECTIVELY.') 
    
    from discord import Embed
    
    with open("keyword_lists/welcome_message.txt", "r", encoding="utf-8") as f:
            raw_message = f.read()
            
    #replace [new user] with actual member name or mention
    personalized_message = raw_message.replace("[new user]", new_member.mention)

    embed_message = Embed(
        title="~From the F2P StarHunt Team~",
        description=personalized_message,
        color=0x1ABC9C)

    return embed_message


class WelcomeDM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #@commands.Cog.listener() registers an event inside a Cog
    #create a welcome message that is DM'd to the user!
    @commands.Cog.listener()
    async def on_member_join(self, member):
        
        try:
            #I only want new members joining F2P StarHunt to trigger this welcome message!
            starhunt_server_id = int(WELCOME_GUILD)

            if member.guild.id != starhunt_server_id:
                return  #ignoreeeeeeee members joining other servers

            channel = None #initialize the variable, in case the first "except" is not triggered

            #create the embed message (nice formatting, 10/10)
            embed_message = prep_welcome_message(member)

            try:
                await member.send(embed=embed_message)
                print(f'Successfully sent DM welcome message to {member.name}!')

            #if user has discord DM privacy settings enabled, just send the message into the channel
            except discord.Forbidden:
                print(f"Could not send DM to {member.name}. Trying #general channel...")  
                channel_id = int(WELCOME_CHANNEL)
                channel = member.guild.get_channel(channel_id)
                await channel.send(embed=embed_message)
                print('Success!')

            except Exception as e:
                print(f"Non-Forbidden error sending DM welcome message to {member.name}: {e}")
                print("Trying #general channel...")

                if channel:
                    await channel.send(embed=embed_message)
                    print('Success!')
                    return

                print('Error sending message, well, anywhere.')
            
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(WelcomeDM(bot))