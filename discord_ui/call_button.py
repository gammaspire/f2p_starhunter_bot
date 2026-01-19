import discord
from discord.ui import Button, View

from universal_utils import world_check_flag
from star_utils import remove_star, add_star_to_list


# custom Discord button class that will allow users to move a star 
# from 'held_stars.json' to 'active_stars.json'
class CallStarButton(Button):
    def __init__(self, username, user_id, world, loc, tier):
        # super() inherits from discord.ui.Button class; calls the parent Button class's constructor
        # if I did not call super(), the button would exist without a label or style...and code may even break
        super().__init__(label='Call Star Now', style=discord.ButtonStyle.green)
        self.world = world
        self.loc = loc
        self.tier = tier
        self.username = username
        self.user_id = user_id
    
    # when I click the button, the star will be removed from the held_stars.json list
    async def callback(self, interaction: discord.Interaction):
        # acknowledge the interaction to avoid timeouts!
        await interaction.response.defer()
        
        try:
            remove_star(self.world, 'held_stars.json')
        except Exception as e:
            print(f'Could not remove held star: {e}')
        
        # if an entry with the same f2p world is not already in the .json file, add it!
        world_check = world_check_flag(self.world, filename='active_stars.json')

        if world_check:
            # star is already active...disable button
            self.disabled = True
            self.style = discord.ButtonStyle.grey
            
            # edit message (that is, change the button and print the confirmation message.)
            await interaction.edit_original_response(view=self.view)
            await interaction.followup.send(f'A star for world {self.world} is already listed!')
            return
        
        # add the star to active list
        add_star_to_list(self.username, self.user_id, self.world, self.loc, self.tier, unix_time=None, 
                         filename='active_stars.json')
        
        # disable the button
        self.disabled = True
        self.style = discord.ButtonStyle.grey
        
        # edit message (that is, change the button and print the confirmation message.)
        await interaction.edit_original_response(view=self.view)
        await interaction.followup.send(f'Star moved to active list!\n'
                                        f'World: {self.world}\nLoc: {self.loc}\nTier: T{self.tier}')


# custom View class that holds the button
class CallStarView(View):
    def __init__(self, username, user_id, world, loc, tier, timeout=600):
        # super() here is inheriting from discord.ui.View, which is the class that handles buttons, 
        # dropdowns, and other UI elements in discord.
        super().__init__(timeout=timeout)
        self.add_item(CallStarButton(username, user_id, world, loc, tier))
        self.message: discord.Message | None = None  # will be set when you send the view

    async def on_timeout(self):
        """Called automatically when the timeout is reached."""
        if self.message:
            #disable all children (buttons, dropdowns, etc.)
            #self.children is built into the View class. it will iterate over all features of the message and disable
            #them if timeous is reached
            for child in self.children:
                child.disabled = True
            try:
                await self.message.edit(view=self)
            except Exception as e:
                print(f"Failed to disable buttons on timeout: {e}")
