#
# Blank Module For Discord Bot
################################
import pickle, sys, time

"""
For a Custom Command !commandMe
"""

async def green(Data, payload, *text):
    pid = payload['Author ID']

    if payload.get('Author') in admins and len(payload['Content'].split(' ')) > 1 : 
        playerid = payload['Content'].split(' ')[1]
        player = await getPlayer(playerid, payload)
        pid = player.id
        print('Setting Color For ',player.name)
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Orange'])
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Purple'])
        await payload['refs']['players'][pid].add_roles(   payload['refs']['roles']['Green'])
        Data['PlayerData'][pid]['Color'] = {'Hue':"Green", "time": time.time() + 24*60*60}

    else time.time() -  Data['PlayerData'][pid]['Color']['time'] > 0 and \
        Data['PlayerData'][pid]['Color']['color'] != "Purple" and \ 
        payload['Channel'] == 'actions':
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Orange'])
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Purple'])
        await payload['refs']['players'][pid].add_roles(   payload['refs']['roles']['Green'])
        Data['PlayerData'][pid]['Color'] = {'Hue':"Green", "time": time.time() + 24*60*60}


async def orange(Data, payload, *text):
    pid = payload['Author ID']

    if payload.get('Author') in admins and len(payload['Content'].split(' ')) > 1 : 
        playerid = payload['Content'].split(' ')[1]
        player = await getPlayer(playerid, payload)
        pid = player.id
        print('Setting Color For ',player.name)
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Green'])
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Purple'])
        await payload['refs']['players'][pid].add_roles(   payload['refs']['roles']['Orange'])
        Data['PlayerData'][pid]['Color'] = {'Hue':"Orange", "time": time.time() + 24*60*60}

    else time.time() -  Data['PlayerData'][pid]['Color']['time'] > 0 and \
        Data['PlayerData'][pid]['Color']['color'] != "Green" and \ 
        payload['Channel'] == 'actions':
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Green'])
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Purple'])
        await payload['refs']['players'][pid].add_roles(   payload['refs']['roles']['Orange'])

        Data['PlayerData'][pid]['Color'] = {'Hue':"Orange", "time": time.time() + 24*60*60}
    

async def purple(Data, payload, *text):
    pid = payload['Author ID']

    if payload.get('Author') in admins and len(payload['Content'].split(' ')) > 1 : 
        playerid = payload['Content'].split(' ')[1]
        player = await getPlayer(playerid, payload)
        pid = player.id
        print('Setting Color For ',player.name)
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Orange'])
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Green'])
        await payload['refs']['players'][pid].add_roles(   payload['refs']['roles']['Purple'])
        Data['PlayerData'][pid]['Color'] = {'Hue':"Purple", "time": time.time() + 24*60*60}

    else time.time() -  Data['PlayerData'][pid]['Color']['time'] > 0 and \
        Data['PlayerData'][pid]['Color']['color'] != "Orange" and \
        payload['Channel'] == 'actions':
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Orange'])
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Green'])
        await payload['refs']['players'][pid].add_roles(   payload['refs']['roles']['Purple'])
        Data['PlayerData'][pid]['Color'] = {'Hue':"Purple", "time": time.time() + 24*60*60}
    


"""
Initiate New Player
"""
async def on_member_join(Data,payload):
    pass


"""
Function Called on Reaction
"""
async def on_reaction(Data, payload):
    pass


"""
Main Run Function On Messages
"""
async def on_message(Data, payload):
    pass


"""
Update Function Called Every 10 Seconds
"""
async def update(Data, payload):
    pass


"""
Setup Log Parameters and Channel List And Whatever You Need to Check on a Bot Reset.
Handles Change In Server Structure and the like. Probably Can Leave Alone.
"""
async def setup(Data,payload):
    pass
