#
# Blank Module For Discord Bot
################################
import pickle, sys, time, re, random, discord, io
import numpy as np
"""
For a Custom Command !commandMe
"""

admins = ['Fenris#6136', 'Crorem#6962', 'iann39#8298', 'Alekosen#6969', None]

async def nick(Data, payload, *text):
    Data['PlayerData'][payload['Author ID']]['Nick'] = payload['Content'][6:]

async def toggleEmoji(Data, payload, *text):
    if payload.get('Author') in admins and len(payload['Content'].split(' ')) == 3: 
        _, playerid, emoji = payload['Content'].split(' ')
        player = await getPlayer(playerid, payload)
        pid = player.id
        print('Toggleing Emoji For',player.name, [hex(ord(i)) for i in emoji])

        if emoji not in Data['PlayerData'][pid]['Emojis']:
            Data['PlayerData'][pid]['Emojis'].append( emoji )
        elif emoji in Data['PlayerData'][pid]['Emojis']:
            try: Data['PlayerData'][pid]['Emojis'].remove( emoji )
            except ValueError: pass
        
        await updateEmojis(Data, payload,)

async def getNewCritic(Data, payload, *text):
    if payload.get('Author') not in admins: return
    optedPlayers = list(Data['Critic']['Opted In'])

    for pid in Data['PlayerData'].keys():
        isInactive = payload['refs']['players'][pid].get_role(payload['refs']['roles']['Inactive'].id) is not None
        if pid in optedPlayers and isInactive: optedPlayers.remove(pid)
    
    activePlayers = list(optedPlayers)

    print('Valid Critics:')
    for pid in Data['Critic']['Banned']:
        if pid in activePlayers: activePlayers.remove(pid)
        else: print('  ', Data['PlayerData'][pid]['Name'])
    
    if len(activePlayers) == 0: 
        Data['Critic']['Banned'] = []
        activePlayers = optedPlayers
        await payload['refs']['channels']['actions'].send('The Critic Pool is Reset!')
    if len(activePlayers) == 0: 
        await payload['refs']['channels']['actions'].send('There are no valid Critic Candidates!')
    else:
        print(len(activePlayers), 'Choices For Critic')
        critic = random.choice(activePlayers)
        Data['Critic']['Banned'].append(critic)
        await payload['refs']['channels']['actions'].send(f'<@{critic}> Is The New Critic!')

    for pid in  Data['PlayerData'].keys():
        if pid in Data['Critic']['Starred']:
            if '⭐' not in Data['PlayerData'][pid]['Emojis']:
                Data['PlayerData'][pid]['Emojis'].append( '⭐' )
        else:
            if '⭐' in Data['PlayerData'][pid]['Emojis']:
                try: Data['PlayerData'][pid]['Emojis'].remove( '⭐' )
                except ValueError: pass
    
    Data['Critic']['Starred'] = []
    await updateEmojis(Data, payload,)


async def optIn(Data, payload, *text):
    if payload['Channel'] != 'Actions':
        if payload['Author ID'] in Data['Critic']['Opted In']:
            await payload['raw'].channel.send('You already opted in, but I like your enthusiasm')
        else:
            Data['Critic']['Opted In'].append( payload['Author ID'] )
            await payload['raw'].channel.send('You are opted in to the Critic Pool')

async def optOut(Data, payload, *text):
    if payload['Channel'] != 'Actions':
        if payload['Author ID'] not in Data['Critic']['Opted In']:
            await payload['raw'].channel.send('You already opted out.')
        else:
            Data['Critic']['Opted In'].remove( payload['Author ID'] )
            await payload['raw'].channel.send('You are opted out of the Critic Pool')


async def getPlayer(playerid, payload):
    if len(playerid) == 0: return None
    else:
        player = payload['refs']['server'].get_member(int(re.search(r'\d+', playerid).group()))
        if player is not None: return player
        else: await payload['raw'].channel.send('Player with id, ' + playerid + ' cannot be found.')
    return None

async def judge(Data, payload, *text):
    pid = payload['Author ID']

    if payload.get('Author') in admins and len(payload['Content'].split(' ')) > 1 : 
        playerid = payload['Content'].split(' ')[1]
        player = await getPlayer(playerid, payload)
        pid = player.id
        print('Setting Judge For ',player.name)
        if payload['refs']['players'][pid].get_role(payload['refs']['roles']['Judge'].id) is None:
            await payload['refs']['players'][pid].add_roles(   payload['refs']['roles']['Judge'])
        else:
            await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Judge'])

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

    elif time.time() -  Data['PlayerData'][pid]['Color']['time'] > 0 and \
        Data['PlayerData'][pid]['Color']['Hue'] != "Purple" and \
        payload['Channel'] == 'actions':
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Orange'])
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Purple'])
        await payload['refs']['players'][pid].add_roles(   payload['refs']['roles']['Green'])
        Data['PlayerData'][pid]['Color'] = {'Hue':"Green", "time": time.time() + 24*60*60}
    else:
        await payload['raw'].channel.send('You cannot be set to this color at this time.')

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

    elif time.time() -  Data['PlayerData'][pid]['Color']['time'] > 0 and \
        Data['PlayerData'][pid]['Color']['Hue'] != "Green" and \
        payload['Channel'] == 'actions':
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Green'])
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Purple'])
        await payload['refs']['players'][pid].add_roles(   payload['refs']['roles']['Orange'])

        Data['PlayerData'][pid]['Color'] = {'Hue':"Orange", "time": time.time() + 24*60*60}
    else:
        await payload['raw'].channel.send('You cannot be set to this color at this time.')

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

    elif time.time() -  Data['PlayerData'][pid]['Color']['time'] > 0 and \
        Data['PlayerData'][pid]['Color']['Hue'] != "Orange" and \
        payload['Channel'] == 'actions':
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Orange'])
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Green'])
        await payload['refs']['players'][pid].add_roles(   payload['refs']['roles']['Purple'])
        Data['PlayerData'][pid]['Color'] = {'Hue':"Purple", "time": time.time() + 24*60*60}
    else:
        await payload['raw'].channel.send('You cannot be set to this color at this time.')

async def removeBuds(Data, payload, *text):
    print('Removing Buds')
    Data['Buddies'] = {'Time Created': 1673244000, 'Buddies' : []}
    await buddify(Data, payload)


async def tally_buds(Data, payload, *text):
    print('Making Buds!')
    for bud in Data['Buddies']['Buddies']:
        basePID = bud[0]
        baseIsGreen  = payload['refs']['players'][basePID].get_role(payload['refs']['roles']['Green'].id) 
        baseIsOrange = payload['refs']['players'][basePID].get_role(payload['refs']['roles']['Orange'].id) 
        baseIsPurple = payload['refs']['players'][basePID].get_role(payload['refs']['roles']['Purple'].id) 

        allSame = True
        for b in bud:
            pid = bud[0]
            isGreen  = payload['refs']['players'][pid].get_role(payload['refs']['roles']['Green'].id) 
            isOrange = payload['refs']['players'][pid].get_role(payload['refs']['roles']['Orange'].id) 
            isPurple = payload['refs']['players'][pid].get_role(payload['refs']['roles']['Purple'].id) 

            if isGreen == baseIsGreen and isOrange == baseIsOrange and isPurple == baseIsPurple: pass
            else: allSame = False
        if allSame:
            for b in bud: Data['PlayerData'][b]['Friendship Tokens'] += 1

async def buddify(Data, payload, *text):
    Data['Buddies']['Time Created'] = ((time.time() - 1673244000)//168 * 60 *60) * 168 * 60 *60 + 1673244000
    Data['Buddies']['Buddies'] = []
    validBuddies = []
    for pid in Data['PlayerData'].keys():
        isInactive = payload['refs']['players'][pid].get_role(payload['refs']['roles']['Inactive'].id) is not None
        if not isInactive: validBuddies.append(pid)
        else: print(Data['PlayerData'][pid]['Name'], 'is inactive bud')
    
    print('Bud Len:', len(validBuddies))
    while len(validBuddies) >= 2:
        bud1 = random.choice(validBuddies)
        validBuddies.remove(bud1)

        bud2 = random.choice(validBuddies)
        validBuddies.remove(bud2)

        Data['Buddies']['Buddies'].append([bud1,bud2])

    if len(validBuddies) == 1 and len(Data['Buddies']['Buddies']) > 0:
        Data['Buddies']['Buddies'][-1].append(validBuddies[0])

    if len(Data['Buddies']['Buddies']) > 0:
        cont = "This Week's Buddies Are:"
        for bud in Data['Buddies']['Buddies']:
            cont += "\n - " 
            for b in bud: cont += f"<@{b}>, "
        await payload['refs']['channels']['actions'].send(cont)
    else: 
        await payload['refs']['channels']['actions'].send('Not enough players for buddies')

async def resetChallenges(Data, payload, *text):
    if payload.get('Author') not in admins: return
    
    if len(payload['Content'].split(' ')) > 1 : 
        playerid = payload['Content'].split(' ')[1]
        player = await getPlayer(playerid, payload)
        pid = player.id
        Data['PlayerData'][pid]['Challanged'] = False

        await payload['raw'].channel.send("Player Challenges Reset.")
    else:
        for pid in Data['PlayerData'].keys():
            Data['PlayerData'][pid]['Challanged'] = False
    
        await payload['refs']['channels']['actions'].send("Gladitorial Challenges Reset.")

async def challenge(Data, payload, *text):
    
    pid = payload['Author ID']
    message = payload['raw']

    if Data['PlayerData'][pid]['Challanged']: 
        await message.channel.send(f"You must wait until next week to challange again")
        return
    
    Data['PlayerData'][pid]['Challanged'] = True
    gladiatorRoll = np.random.randint(1, 101, 1)
    playerRoll    = np.random.randint(1, 25, 1)
    if playerRoll > gladiatorRoll:
        await message.channel.send(f"Gladiator: {gladiatorRoll}\nPlayer {playerRoll}\n{payload['Author']} Wins")
        
        player = payload['raw'].author
        gldetr = payload['refs']['players'][Data['Gladiator']['Player']]

        pid = player.id
        gid = gldetr.id

        if '⚔️' not in Data['PlayerData'][pid]['Emojis']:
            Data['PlayerData'][pid]['Emojis'].append( '⚔️' )
        
        if '⚔️' in Data['PlayerData'][gid]['Emojis']:
            try: Data['PlayerData'][gid]['Emojis'].remove( '⚔️' )
            except ValueError: pass


        print(player.nick, gldetr.nick)
        Data['Gladiator'] = {'Player': pid, 'DOB':Data['Turn']+1}
        await updateEmojis(Data, payload,)
    else: 
        await message.channel.send(f"Gladiator: {gladiatorRoll}\nPlayer {playerRoll}\n{payload['Author']} Is Defeated")

async def updateEmojis(Data, payload):
    for pid in Data['PlayerData'].keys():
        player = payload['refs']['players'][pid]
        emojis = ''.join(sorted(Data['PlayerData'][pid]['Emojis'])).replace(' ','')
        
        nickname = Data['PlayerData'][pid]['Nick'] + emojis
        nickname = nickname.replace('\uFE0F','').replace('\uFE0E','')
        old_nick = player.nick
        if old_nick == None: old_nick = player.name
        if nickname != old_nick:
            if Data['admin'] == pid:    pass #await player.send(f"As admin, you must set your nick to {nickname}")
            else:                       
                print(nickname, old_nick, '\n',str.encode(nickname), '\n', str.encode(old_nick), '\n' )
                await player.edit(nick = nickname)

async def setTokens(Data, payload, *text):
    if payload.get('Author') not in admins: return
    
    cont = payload['Content'].strip().split(' ')
    if len(cont) > 2 : 
        playerid = payload['Content'].split(' ')[1]
        player = await getPlayer(playerid, payload)
        pid = player.id

        toset = 0
        try: toset = int(cont[2])
        except ValueError: return

        Data['PlayerData'][pid]['Friendship Tokens'] = toset

async def setGladiator(Data, payload, *text):
    if payload.get('Author') not in admins: return
    
    cont = payload['Content'].strip().split(' ')
    if len(cont) > 1: 
        playerid = payload['Content'].split(' ')[1]

        player = await getPlayer(playerid, payload)

        pid = player.id
        gid = Data['Gladiator']['Player']

        if gid is not None:
            gldetr = payload['refs']['players'][Data['Gladiator']['Player']]
            if gldetr.nick is not None and '⚔' == gldetr.nick[-1]:
                print(gldetr.nick[-1], )
                if Data['admin'] == gid:    await gldetr.send("As admin, you must remove ⚔️ from your nick")
                else:                       await gldetr.edit(nick = gldetr.nick[:-1])

        if player.nick is     None or  '⚔' != player.nick[-1]:
            if Data['admin'] == pid:    await player.send("As admin, you must add ⚔️ to you nick")
            else:
                if player.nick is None: await player.edit(nick = player.name+'⚔️' )
                else:                   await player.edit(nick = player.nick+'⚔️' )

        Data['Gladiator'] = {'Player': pid, 'DOB':Data['Turn']+1}

async def give(Data, payload, *text):
    playerid = payload['Content'].split(' ')[1]
    player = await getPlayer(playerid, payload)
    pid = player.id

    if Data['PlayerData'][payload['Author ID']]['Friendship Tokens'] <= 0: 
        await payload['raw'].add_reaction('❌')
        return

    Data['PlayerData'][pid]['Friendship Tokens'] += 1
    Data['PlayerData'][payload['Author ID']]['Friendship Tokens'] -= 1

async def setOffer(Data, payload, *text):
    if payload.get('Author') not in admins: return
    
    cont = payload['Content'].strip().split(' ')
    if len(cont) > 2 : 
        playerid = payload['Content'].split(' ')[1]
        player = await getPlayer(playerid, payload)
        pid = player.id

        toset = 0
        try: toset = int(cont[2])
        except ValueError: return

        Data['PlayerData'][pid]['Offers'] = toset


async def offer(Data, payload, *text):
    if payload['Channel'] != "market": return
    pid = payload['Author ID']
    offerd = 0
    text = text[0]


    if len(text) <= 3: 
        await payload['raw'].author.send("Your Offer Doesnt Have The Correct Format.")
        await payload['raw'].add_reaction('❌')
        return          

    try:   offerd = int(text[2])
    except ValueError: 
        await payload['raw'].author.send("Your Offer Doesnt Have The Correct Format.")
        await payload['raw'].add_reaction('❌')
        return          


    if offerd + Data['PlayerData'][pid]['Offers'] > Data['PlayerData'][pid]['Friendship Tokens']:
        await payload['raw'].author.send("You do not have enough Friendship Tokens to make that offer")
        await payload['raw'].add_reaction('❌')
        return
    
        
    await payload['raw'].add_reaction('✔️')
    Data['PlayerData'][pid]['Offers'] += offerd

async def acceptOffer(Data, payload):
    offerd = 0
    text   = payload['message'].content[1:].split(' ')

    try:    offerd = int(text[1])
    except: return

    if '@' in payload['message'].content[1:].split(' ')[1] and f"{payload['user'].id}" != payload['message'].content[1:].split(' ')[2:-1]:
        await payload['raw'].author.send("You cannot accept that offer.")
        return
    
    files  = [discord.File(fp=io.StringIO(payload['message'].content), filename="Terms_Of_Offer.txt"),]
    await payload['refs']['channels']['actions'].send(f"<@{payload['message'].author.id}>'s Offer Has Been Accepted By <@{payload['user'].id}> for {offerd} Tokens", files = files)
    await payload['message'].delete()

async def payOffer(Data, payload):
    print('Paying', payload['message'].content)
    if "Offer Has Been Accepted By" in payload['message'].content:
        payer = int(payload['message'].content.split('@')[1].split('>')[0])
        payee = int(payload['message'].content.split('@')[2].split('>')[0])
        amount = int(payload['message'].content.split(' ')[-2])


        Data['PlayerData'][payee]['Friendship Tokens'] += amount
        Data['PlayerData'][payer]['Friendship Tokens'] -= amount
        Data['PlayerData'][payer]['Offers'] -= amount

        await payload['message'].edit(content=f"<@{payer}>'s Offer Has Been Accepted and Completed By <@{payee}> for {amount} Tokens")
        await payload['refs']['channels']['actions'].send(f"<@{payer}>'s Offer Has Been Completed By <@{payee}>")
    


async def me(Data, payload, *text):
    pid = payload['Author ID']
    cont =      "Your Info\n```" 
    cont +=    f" Friendship Tokens:  {Data['PlayerData'][pid]['Friendship Tokens']}\n" 
    cont +=    f" Has Challenged:     {Data['PlayerData'][pid]['Challanged']}\n" 
    cont +=    f" Tokens Offered:     {Data['PlayerData'][pid]['Offers']}\n" 
    cont +=    f" Opted In To Critic: {pid in Data['Critic']['Opted In']}\n" 
    cont +=    "```"
    await payload['raw'].author.send(cont )

async def all(Data, payload, *text):
    for pid in Data['PlayerData'].keys():
        cont =     f"{Data['PlayerData'][pid]['Nick']}:\n```" 
        cont +=    f" Friendship Tokens: {Data['PlayerData'][pid]['Friendship Tokens']}\n" 
        cont +=    f" Has Challenged:    {Data['PlayerData'][pid]['Challanged']}\n" 
        cont +=    f" Tokens Offered:    {Data['PlayerData'][pid]['Offers']}\n" 
        cont +=    f" Opted In To Critic: {pid in Data['Critic']['Opted In']}\n" 
        cont +=    "```"
        await payload['raw'].channel.send(cont )

"""
Initiate New Player
"""
async def on_member_join(Data,payload):
    pass


"""
Function Called on Reaction
"""
async def on_reaction(Data, payload):
    if payload['emoji'] == '✔️' and payload['Channel'] == 'market':
        await acceptOffer(Data, payload)
    if payload['emoji'] == '✔️' and payload['Channel'] == 'actions' and f"{payload['user'].name}#{payload['user'].discriminator}" in admins:
        await payOffer(Data, payload)
    if payload['message'].id == Data['Wizard']['MSG']:
        Data['Wizard']['MSG'] = None
        
        basePID = payload['user'].id
        baseIsGreen  = payload['refs']['players'][basePID].get_role(payload['refs']['roles']['Green'].id) 
        baseIsOrange = payload['refs']['players'][basePID].get_role(payload['refs']['roles']['Orange'].id) 
        baseIsPurple = payload['refs']['players'][basePID].get_role(payload['refs']['roles']['Purple'].id) 

        for pid in  Data['PlayerData'].keys():
            isGreen  = payload['refs']['players'][pid].get_role(payload['refs']['roles']['Green'].id) 
            isOrange = payload['refs']['players'][pid].get_role(payload['refs']['roles']['Orange'].id) 
            isPurple = payload['refs']['players'][pid].get_role(payload['refs']['roles']['Purple'].id) 

            if isGreen == baseIsGreen and isOrange == baseIsOrange and isPurple == baseIsPurple: 
                Data['PlayerData'][pid]['Emojis'].append( '🧙' )
           
    if payload['emoji'] == '✔️' and payload['Channel'] == 'critic-responses':
        Data['Critic']['Starred'].append(payload['message'].author.id)

"""
Main Run Function On Messages
"""
async def on_message(Data, payload):
    pass


"""
Update Function Called Every 10 Seconds
"""
async def update(Data, payload):
    if  Data['Gladiator']['Player'] not in ['', None] and Data['Gladiator']['DOB'] + 1 == Data['Turn']:
        Data['Gladiator']['DOB'] += 1
        Data['PlayerData'][Data['Gladiator']['Player']]['Friendship Tokens'] += 1
    if time.time() - Data['Wizard']['Time'] > 3600 and False:
        Data['Wizard']['Time'] = (time.time()//3600)*3600
        if int(np.random.random()*100) == 0 :
            Data['Wizard']['Time'] = ((time.time() - 1673244000)//(168 * 60 *60)) * 168 * 60 *60 + 1673244000
            msg  = await payload['refs']['channels']['game'].send('GOLDEN SNITCH')
            Data['Wizard']['MSG'] = msg.id
            for pid in  Data['PlayerData'].keys():
                try: Data['PlayerData'][pid]['Emojis'].remove( '🧙' )
                except ValueError: pass
    
    await updateEmojis(Data, payload,)

"""
Setup Log Parameters and Channel List And Whatever You Need to Check on a Bot Reset.
Handles Change In Server Structure and the like. Probably Can Leave Alone.
"""
async def setup(Data,payload):
    pass
