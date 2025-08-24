'''
AIM: pull list of active F2P worlds from OSRS and save them into a .txt file (one world per row).
Note that each 'world' corresponds to Jagex' world ID. In order to convert this ID to an actual world, we need to calculate 
World ID + 300. 

NOTE: this function is sort of part utility, part standalone. As such, its home is currently in the parent directory, having been given the charmed "misfit" status as with discord_ui.py. I do plan to utilize this function further for a side-project involving the monitoring of worlds when certain (or all?) servers are down for temporary maintenance. The problem is that the bot would have to pull from the Jagex website every...couple of seconds...to check if there are dips in the player count from non-zero to zero to non-zero. So, who knows if I will actually pursue this? Certainly not me.
'''

def pull_f2p_worlds():

    import requests
    from bs4 import BeautifulSoup   #a helpful package for parsing/reading html text.

    #the url from which to pull the list of worlds
    url = "https://oldschool.runescape.com/slu"

    #actually pull the data
    res = requests.get(url)

    #parse it!
    soup = BeautifulSoup(res.text, "html.parser")

    #locate the table (which contains worlds, etc.)
    rows = soup.select("table tr")

    #create empty f2p worlds list
    f2p_worlds = []

    #for every row in rows, which contains information about world, # current players, 
    #whether the world is free/members, and what "activity" it features
    for row in rows:

        #strip the row into its components
        #example: ['Old School 89', '627 players', 'Australia', 'Members', 'Wintertodt']
        cols = [td.get_text(strip=True) for td in row.find_all("td")]

        #if there is no output column, just skip to the next row
        if not cols:
            continue

        #pull the world and type_ (use type_ instead of type, since type is a pre-built command in python. silly.
        world, _, _, type_, _ = cols[0], cols[1], cols[2], cols[3], cols[4]
        if "Free" in type_:
            #replace the pretext with blanks, otherwise each row will have 'Old School [world]' or 'OldSchool [world]
            world = world.replace('Old School ', '')
            world = world.replace('OldSchool ','')
            f2p_worlds.append(f"{int(world)+300}")

    #(over)write and save!
    with open('keyword_lists/active_f2p_worlds.txt', "w") as f:
        f.write("\n".join(f2p_worlds))