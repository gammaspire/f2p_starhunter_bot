from universal_utils import load_json_file
from discord.ext import commands

import sys
sys.path.insert(0,'discord_ui')
from refresh_button import RefreshView


#this function restores the hoplist message refresh button!
async def restore_hoplist_view(bot: commands.Bot):
    """
    Attempt to restore previously-posted hoplist message(s) + the RefreshView after bot restart.
    called from main.py to reattach the view(s) to the message(s) saved in keyword_lists/hoplist_messages.json
    Does not return anything; views are attached in place and will function.
    """
    
    button_file = 'keyword_lists/hoplist_messages.json'
    
    #try first to load the "state(s)" (each include message_id, channel_id, message_count...)
    states = load_json_file(button_file)
    if not states:       #checks if dictionary is empty. fun bool logic occurring here.
        return

    #normalize: if the file only has one dict, wrap it in a list
    if isinstance(states, dict):
        states = [states]

    #iterate through all saved states
    for state in states:
        
        try:
            channel_id = state.get('channel_id')
            message_id = state.get('message_id')
            refresh_count = int(state.get('refresh_count', 0))   #grab refresh count if it exists; if not, just default to zero

            if channel_id is None or message_id is None:
                continue #next state. just means there are no messages to update! (or the file was corrupted somehow...etc.

            channel = bot.get_channel(channel_id)
            
            if channel is None:
                print(f"Could not find channel id {channel_id} to restore the Hoplist message.")
                continue #next staaate.

            msg = await channel.fetch_message(message_id)
            if msg is None:
                print(f"Could not fetch message in channel {bot.get_channel(channel_id).name} to restore the Hoplist message.")
                continue  #...next state

            view = RefreshView()
            view.message = msg
            view.refresh_count = refresh_count

            try:
                await msg.edit(view=view)
                print(f"Restored hoplist refresh button and count in channel #{bot.get_channel(channel_id).name}.")
            
            except Exception as e:
                print(f"Could not attach view to Hoplist message: {e}")
                #continue to next state...even if Exception is raised.
        
        except Exception as e:
            print(f"Could not restore hoplist view: {e}")
            continue
