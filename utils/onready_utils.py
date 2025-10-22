'''
Various utility functions that will run when the bot activates!
'''

################################################################################
#loading the COGS!
#each Cog is a bot command or event! this function simply loads them for use.
################################################################################
async def load_cogs(bot):
    import os
    for folder, prefix in [("./commands", "commands"), ("./events", "events"), ("./Halloween2025", "Halloween2025")]:
        for filename in os.listdir(folder):
            if filename.endswith(".py") and filename != "__init__.py":
                #in /commands, I have __init__.py, so python treats /commands as a package
                #every .py file is its own Class, just like numpy.array or scipy.stats
                #as such, I load the extension as commands._____, with the [:-3] removing the '.py'
                ext_name = f"{prefix}.{filename[:-3]}"
                if ext_name not in bot.extensions:
                    await bot.load_extension(ext_name)


################################################################################
#syncing the slash commands!
#each Cog is a bot command or event! this function simply loads them for use.
################################################################################
async def sync_commands(bot, guild):
    #this will sync the commands with Discord's API.
    #it is recommended to do this only once or when you change commands.
    #if you have a lot of commands, you might want to use `sync(guild_id=GUILD_ID)` to sync only for a specific guild.
    #replace GUILD_ID with your actual guild ID if you want to limit the sync.
    #for global commands, you can use `bot.tree.sync()` without any parameters.
    #note: Global commands *can* take up to an hour to propagate.  
    try:
        synced = await bot.tree.sync(guild=guild)   #if guild=None, then sync is global
                                                    #for Tester Bot, I specify a guild.
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")
                    
                    
################################################################################
#creating and sending the onready message!
#this is only applicable if I am running Tester Bot.
################################################################################
async def onready_message(bot, ctx_id):

    channel = bot.get_channel(ctx_id)

    if channel:
        await channel.send("A FRIENDLY REMINDER!\n\n" 
                           "As the Tester Bot, I am reading from and writing to [this Google Sheet](<https://docs.google.com/spreadsheets/d/1i52-v3hCBZlFQong3EFyHZtc3rP47njUEDsWAV6_FoU/edit?gid=930734666#gid=930734666>), the testing equivalent to [loon.dust.wiki](<https://docs.google.com/spreadsheets/d/1mNLGnXrlr4v-8dzM-4xQp7YpMq4D34Dnaaengs-jXeo/edit?gid=0#gid=0>).\n\n"
                          "I am also using a different Google Service Account to my esteemed colleague, F2P Starhunter (known affectionately as bot-kun). See notes.txt for further details.\n\n"
                           "-# If you do not know what notes.txt refers to, this message was not meant for you. Cope.")
    else:
        print(f"Error: Channel with ID {channel} not found.")