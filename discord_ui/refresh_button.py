import discord
from discord.ui import Button, View
import time

from hoplist_utils import send_hoplist_message
from universal_utils import load_json_file, save_json_file

button_file = 'keyword_lists/hoplist_messages.json'



class RefreshButton(Button):
    def __init__(self):
        super().__init__(label="🔄 REFRESH 🔄", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        now = time.time()
        
        try:
            #add 1 to the total refresh count!
            if isinstance(self.view, RefreshView):
                
                if (now - self.view.last_click) < self.view.cooldown:
                    await interaction.followup.send(
                        f"-# Woah there, Lightning McQueen. Please wait {self.view.cooldown} seconds between refreshes.", 
                        ephemeral=True)
                        
                    return
                
                self.view.last_click = now
                self.view.refresh_count += 1
            
            #resend hoplist in same channel (edit original message instead of sending a new one)
            await send_hoplist_message(channel=interaction.channel, message_id=interaction.message.id,
                interaction=interaction, refresh_count=self.view.refresh_count)
            
            #write and save message ID, channel ID, and refresh count
            try:
                states = load_json_file(button_file) or []
                
                #check if the state already exists! 
                for state in states:
                    #check if the message_id is the same as the one for which the button was clicked
                    if state.get('message_id') == interaction.message.id:
                        #update the refresh count if found
                        state['refresh_count'] = self.view.refresh_count
                        #no need to continue looping because we found the message, laddies
                        break
                else:
                    #if it does not yet exist, add the new message/channel/count/whatever
                    states.append({'message_id': interaction.message.id,
                                   'channel_id': interaction.channel.id,
                                   'refresh_count': self.view.refresh_count})
                
                save_json_file(states, button_file)
            
            except Exception as e:
                print(f"Refresh Button failed to persist state after refresh: {e}")
            
        except Exception as e:
            print(f"Error in RefreshButton: {e}")
            await interaction.followup.send("Could not refresh hoplist.", ephemeral=True)

        #await interaction.followup.send("Hoplist is refreshed. Happy scouting!", ephemeral=True)



class RefreshView(View):
    def __init__(self):
        
        super().__init__(timeout=None)
        
        self.add_item(RefreshButton())
        self.message: discord.Message | None = None   #this will be set once the RefreshView is run
        self.refresh_count: int = 0   #tracks how many times the button has been clicked. begin at zero!
        
        #implementing a cooldown time!
        #users cannot click the button consecutively until at least five seconds have passed.
        self.last_click: float = 0  #stores timestamp of last click. begin at zero!
        self.cooldown: float = 5.0      #cooldown in seconds