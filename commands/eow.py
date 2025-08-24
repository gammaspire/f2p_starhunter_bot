############################################################
#Print the current call time estimate for a star given its
#world and tier!
#use: 
#   $eow world tier
#e.g., '$eow 308 7' (for a t7 star in world 308)
############################################################

from discord.ext import commands
import sys

sys.path.insert(0, '../utils')
from universal_utils import remove_frontal_corTex, load_f2p_worlds
from googlesheet_utils import get_call_time, get_wave_time


def create_eow_message(world_string, tier_string):
    
    #remove any t or T prefix
    tier_string = remove_frontal_corTex(tier_string)
    
    #TIER 6 -- B, TIER 7 -- C, TIER 8 -- D, TIER 9 -- E        
    #if tier is not one of the default 4, wir haben einen Problem. 
    if int(tier_string) not in [6,7,8,9]:
        return 'Tier must be 6, 7, 8, or 9. Please and thank you.'
    
    #also...if world not found, or f2p world is temporarily a p2p world, toss this error to the user
    if world_string not in load_f2p_worlds():
        return 'Use a valid F2P world!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! It is not that difficult, I promise.'
    
    
    #otherwise...prints call time for world and current wave time.
        
    try:
        
        call_time = get_call_time(world_string,tier_string)
                
        #if the call time is *85*, then we do not yet have poof data for that world
        #for the purposes of collecting poof data, hold star until +85 unless backup is needed immediately
        if call_time=='*85*':
            return f'Poof data for {world_string} is TBD. Please default to holding until +85 into the wave.' 
        else:
            wave_time = get_wave_time()
            
            #call_time in the cell is +xx, so remove + to convert to integer
            #otherwise...please hold the star. :-)  
            if int(wave_time)<int(call_time.replace('+','')):
                call_notice = f"Please hold for {int(call_time.replace('+','')) - int(wave_time)} minutes."

            #if the wave time is larger than the call time, then I can call the star! 
            else:
                call_notice = f'You can call the star now!'

            return f'The suggested call time for {world_string} T{tier_string} is {call_time}. The current wave time is +{wave_time}. {call_notice}'
    
    #otherwise...prints call time for world and current wave time.
    except:
        return f"For Pete's sake, PLEASE use a valid F2P world."


class Eow(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(help='Prints suggested EOW call time for the entered world. If no poof time is recorded for that world, then defaults to +85. Tiers 6-9 only.\nExample usage: $eow 308 9')
    async def eow(self, ctx, world=None, tier=None):
        
        if (world is None) or (tier is None):
            await ctx.send('The correct syntax is $eow [world] [tier]. Wanna try that again?')
            return
        
        call_message = create_eow_message(world, tier)
        await ctx.send(call_message)
            
            
async def setup(bot):
    await bot.add_cog(Eow(bot))