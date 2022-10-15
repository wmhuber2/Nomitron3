#
# Voting System Module For Discord Bot
################################
import pickle, sys, time, io, discord, datetime, urllib, re, random
tz = datetime.timezone.utc
"""
For a Custom Command !commandMe
"""


clearOnStart = True
admins = ['Fenris#6136', 'Crorem#6962', 'iann39#8298', 'Alekosen#6969', None]

zeroday = 1641016800 # Jan 1 2022
day  = 60*2 # 24 * 60 * 60
def now(): return time.time() - zeroday


async def turnStats(Data, payload, *text):
    msg = f'''**Turn Stats:**```
    Proposal#            :   {Data['Proposal#']}
    Voting Enabled       :   {Data['VotingEnabled']}
    Proposing Player     :   {Data['ProposingPlayer']}
    Curr Turn Start Time :   {Data['CurrTurnStartTime']}
    Next Turn Start Time :   {Data['NextTurnStartTime']}
    Time Now             :   {now()} (Raw:{time.time()})
    Time Elapsed         :   {now() - Data['CurrTurnStartTime']}
    Time Remaining       :   {Data['NextTurnStartTime'] - now()}
    Votes                :   {Data['Votes']}
    ```'''
    await payload['raw'].channel.send(msg)

async def removeSupporter(Data, payload, *text):
    if payload.get('Author') not in admins: return

    playerid, nth = payload['Content'].split(' ')[1:3]
    player = await getPlayer(playerid, payload)
    pid = player.id
    nth = int(nth)
    print(f"Purging {nth} {Data['PlayerData'][pid]['Proposal']['Supporters'][nth]} supporter for {player.name}")

    Data['PlayerData'][pid]['Proposal']['Supporters'].pop(nth)
    return Data

async def extendTurn(Data, payload, *text):
    if payload.get('Author') not in admins: return

    Data['NextTurnStartTime'] += day
    await payload['raw'].channel.send('Turn extended 24 hrs. Use !tickTurn to manually trigger the next turn if needed')
    return Data

async def removeProposal(Data, payload, *text):
    if payload.get('Author') not in admins: return 

    playerid = payload['Content'].split(' ')[1]
    player = await getPlayer(playerid, payload)
    pid = player.id
    print('Purging proposals for ',player.name)

    Data['PlayerData'][pid]['Proposal'] = {}
    Data['PlayerData'][pid]['Proposal']['File'] = ''
    Data['PlayerData'][pid]['Proposal']['Supporters'] = []
    Data['PlayerData'][pid]['Proposal']['DOB'] = now()

    await create_queue(Data, payload)

async def getPlayer(playerid, payload):
    if len(playerid) == 0: return None
    else:
        player = payload['refs']['server'].get_member(int(re.search(r'\d+', playerid).group()))
        if player is not None: return player
        else: await channel.send('Player with id, ' + playerid + ' cannot be found.')
    return None

async def tickTurn(Data, payload, *text):
    print('..Turn Ticking')

    await bot_tally(Data, payload)
    await popProposal(Data, payload)

    if payload.get('Author') not in admins: return

    if len(Data['ProposingText']) < 1:  Data['NextTurnStartTime'] = (now()//day  + 1) * day
    else:                               Data['NextTurnStartTime'] = (now()//day  + 2) * day
    Data['CurrTurnStartTime'] = (now()//day) * day
    Data['VotingEnabled'] = False
    Data['Turn'] += 1

async def setProp(Data, payload, *text):
    if payload.get('Author') not in admins: return
    try: Data['Proposal#'] = int(text[0][1])
    except Exception as e: print(e)
    await payload['raw'].channel.send(f"Set Proposal to {Data['Proposal#']}")

async def bot_tally(Data, payload, *text):
    if payload.get('Author') not in admins: return
    if len(Data['ProposingText']) < 1:
        await payload['refs']['channels']['actions'].send(f"**Start Of New Turn #{Data['Turn']}. No Proposal was on Deck**")
        return
    player = Data['ProposingPlayer']

    if len(Data['Votes']['Yay']) > len(Data['Votes']['Nay']):
        await payload['refs']['channels']['actions'].send(f"""**Start Of New Turn #{Data['Turn']}. {player}'s Proposal Passes
        Tally: {len(Data['Votes']['Yay'])} For, {len(Data['Votes']['Nay'])} Against.**
        """)
    else:
        await payload['refs']['channels']['actions'].send(f"""**Start Of New Turn #{Data['Turn']}. {player}'s Proposal Failed
        Tally: {len(Data['Votes']['Yay'])} For, {len(Data['Votes']['Nay'])} Against.**
        """)

def proposalText(Data):
    playerprop = Data['ProposingPlayer']
    if playerprop is None: return []

    msg = f"Proposal #{Data['Proposal#']}: "
    if Data['VotingEnabled']: msg += f"**Status: ({len(Data['Votes']['Yay'])} For, {len(Data['Votes']['Nay'])} Against.)** \n\n "
    else                    : msg += "**Status: ON DECK (No Voting)** \n\n "
    topin = []

    for line in Data['ProposingText'].split('\n'):
        line += '\n'
        if len(msg + line) > 1950:
            topin.append(msg)
            msg = ""
        else: msg += line
    if len(msg) > 1: topin.append(msg)
    return topin

async def updateProposal(Data, payload):
    print('..Updating Prop')
    if payload.get('Author') not in admins: return

    if Data['VotingEnabled']:
        lines = proposalText(Data)
        for i in range(len(Data['ProposingMSGs'])): 
            mid  = Data['ProposingMSGs'][i] 
            msg = await payload['refs']['channels']['voting'].fetch_message(mid) 
            line = lines[i]
            await payload['refs']['channels']['voting'].edit(line)
    else:
        for mid in Data['ProposingMSGs']: 
            msg = await payload['refs']['channels']['voting'].fetch_message(mid) 
            await msg.delete()

        Data['ProposingMSGs'] = []
        for line in proposalText(Data):
            msg = await payload['refs']['channels']['voting'].send(line)
            Data['ProposingMSGs'].append(msg.id)

async def enableVoting(Data, payload, *text):
    print('..Enabling Voting')
    Data['VotingEnabled'] = True

    await payload['refs']['channels']['voting'].set_permissions(payload['refs']['roles']['Player'], send_messages=True)
    await payload['refs']['channels']['actions'].send("Players May Now Vote in #voting.")
    for p in payload['refs']['players'].values(): await p.remove_roles(payload['refs']['roles']['On Deck'])

async def popProposal(Data, payload, *text):
    if payload.get('Author') not in admins: return
 
    Data['ProposingPlayer'] = None
    Data['ProposingText']   = ""
    await payload['refs']['channels']['voting'].set_permissions(payload['refs']['roles']['Player'], send_messages=False)

    print('..PopProposal To Deck:')
    if len(Data['Queue']) == 0: return Data
    pid = Data['Queue'].pop(0)
    print('...',pid, Data['PlayerData'][pid]['Name'])


    if len(Data['PlayerData'][pid]['Proposal']['File']) <= 1: return Data

    for p in payload['refs']['players'].values(): await p.remove_roles(payload['refs']['roles']['On Deck'])
    await payload['refs']['players'][pid].add_roles(payload['refs']['roles']['On Deck'])
    
    Data['Votes'] = { 'Yay':[], 'Nay':[], 'Abstain':[] }
    Data['Proposal#']       += 1
    Data['ProposingPlayer']  = pid
    Data['ProposingText']    = str(Data['PlayerData'][pid]['Proposal']['File'])

    Data['PlayerData'][pid]['Proposal']['File'] = ''
    Data['PlayerData'][pid]['Proposal']['Supporters'] = []
    Data['PlayerData'][pid]['Proposal']['DOB'] = now()

    await updateProposal(Data, payload)
    await create_queue(Data, payload, )

async def yay(Data, payload):
    author = payload['Author ID']
    if author not in Data['Votes']['Yay']:           Data['Votes']['Yay'].append( author )
    if author in Data['Votes']['Nay']:               Data['Votes']['Nay'].remove( author )
    if author in Data['Votes']['Abstain']:           Data['Votes']['Abstain'].remove( author )
    #await payload['message'].remove_reaction(nayEmoji , payload['user'])

async def nay(Data, payload):
    author = payload['Author ID']
    if author not in Data['Votes']['Nay']:           Data['Votes']['Nay'].append( author )
    if author in Data['Votes']['Yay']:               Data['Votes']['Yay'].remove( author )
    if author in Data['Votes']['Abstain']:           Data['Votes']['Abstain'].remove( author )
    #await payload['message'].remove_reaction(yayEmoji , payload['user'])

async def abstain(Data, payload):
    author = payload['Author ID']
    if author not in Data['Votes']['Abstain']:       Data['Votes']['Abstain'].append( author )
    if author in Data['Votes']['Yay']:               Data['Votes']['Yay'].remove( author )
    if author in Data['Votes']['Nay']:               Data['Votes']['Nay'].remove( author )
    #await payload['message'].remove_reaction(yayEmoji , payload['user'])
    #await payload['message'].remove_reaction(nayEmoji , payload['user'])

"""
Function Called on Reaction
"""
async def on_reaction(Data, payload):
    if payload['Channel'].name == 'voting' and False:
       
        if payload['emoji'] == yayEmoji:
            await yay(Data, payload)
            await payload['raw'].add_reaction('✔️')
        if payload['emoji'] == nayEmoji:            
            await nay(Data, payload)
            await payload['raw'].add_reaction('✔️')
        elif vote in ['abstain', 'withdraw']:
            await abstain(Data, payload)
            await payload['raw'].add_reaction('✔️')

    if payload['Channel'].name == 'queue' and payload['mode'] == 'add':

        await payload['message'].remove_reaction(payload['emoji'] , payload['user'])
        if len(payload['Attachments']) == 0: return Data
        author   = int(list(payload['Attachments'].keys())[0].split("-")[0])
        
        if payload['emoji'] == '👍':
            if payload['user'].id not in Data['PlayerData'][author]['Proposal']['Supporters']:
                Data['PlayerData'][author]['Proposal']['Supporters'].append(payload['user'].id)
            await create_queue(Data, payload)

        if payload['emoji'] == '👎':
            if payload['user'].id in Data['PlayerData'][author]['Proposal']['Supporters']:
                Data['PlayerData'][author]['Proposal']['Supporters'].remove(payload['user'].id)
            await create_queue(Data, payload)

        if payload['emoji'] == 'ℹ️':
            msg =   f"------\n **{Data['PlayerData'][author]['Name']}'s Proposal Info:**\n```Supporters:"
            for p in Data['PlayerData'][author]['Proposal']['Supporters']: msg += '\n - ' + Data['PlayerData'][p]['Name']
            msg += "```"
            await payload['user'].send(msg)

            msg = "**\nProposal:**\n"
            for line in Data['PlayerData'][author]['Proposal']['File'].split('\n'):
                line += '\n'
                if len(msg + line) > 1900:
                    await payload['user'].send(msg)
                    while len(line) > 1900:
                        msgend = line[1900:].index(' ')
                        await payload['user'].send(line[:1900+msgend])
                        line = line[1900+msgend:]
                    msg = line
                else: msg += line
            if len(msg) > 0: await payload['user'].send(msg)
    return Data


"""
Main Run Function On Messages
"""
async def on_message(Data, payload):
    if payload['Channel'] == 'voting':

        # Remove MSG if from a non Player (Bot, Illegal, Etc)
        if payload['Author ID'] not in Data['PlayerData'] or not Data['VotingEnabled']:
            print('Removing', payload['Content'])
            await payload['raw'].delete()
            return
            
        # Register Vote
        vote = payload['Content'].lower().strip()
        if vote in ['y', 'yay', 'aye', 'yes']:
            await yay(Data, payload)
            await payload['raw'].add_reaction('✔️')
        elif vote in ['nay', 'no', 'n']:
            await nay(Data, payload)
            await payload['raw'].add_reaction('✔️')
        elif vote in ['abstain', 'withdraw']:
            await abstain(Data, payload)
            await payload['raw'].add_reaction('✔️')
        else:
            await payload['raw'].add_reaction('❌')
            await payload['raw'].author.send( content = "Your vote is ambigious, Pleas use appropriate yay, nay, or withdraw text." )

        updateProposal(Data, payload)

    if payload['Channel'] == 'proposals':
        print('Saving Proposal', payload['Content'])
        pid = payload['Author ID']

        if len(payload['Attachments']) == 1 and '.txt' in list(payload['Attachments'].keys())[0]:
            decoded = await list(payload['Attachments'].values())[0].read()
            decoded = decoded.decode(encoding="utf-8", errors="strict")
            Data['PlayerData'][pid]['Proposal']['File'] = decoded

        if len(payload['Attachments']) == 0:
            Data['PlayerData'][pid]['Proposal']['File'] = payload['Content']

        print("Prop:", Data['PlayerData'][pid]['Proposal']['File'])
        Data['PlayerData'][pid]['Proposal']['DOB'] = now()
        Data['PlayerData'][pid]['Proposal']['Supporters'] = [pid, ]
        await create_queue(Data, payload, )

    if payload['Channel'] == 'deck-edits':
        print('Updating Proposal')
        if payload['Author ID'] != Data['ProposingPlayer'] or Data['VotingEnabled'] == True: 
            await payload['refs']['channels']['deck-edits'].send("The deck cannot be updated at this time in the turn.")
            return

        if len(payload['Attachments']) == 1 and '.txt' in list(payload['Attachments'].keys())[0]:
            decoded = await list(payload['Attachments'].values())[0].read()
            decoded = decoded.decode(encoding="utf-8", errors="strict")
            Data['ProposingText'] = decoded

        if len(payload['Attachments']) == 0:
            Data['ProposingText'] = payload['Content']
        await updateProposal(Data, payload, )
    
    return Data

"""
Update Function Called Every 10 Seconds
"""
async def update(Data, payload):
    if   (now() - Data['NextTurnStartTime'] > 0):
        print('..Updating TickTurn')
        await tickTurn(Data, payload)
    elif (now() - Data['CurrTurnStartTime'] > day) and (not Data['VotingEnabled']):
        await enableVoting(Data, payload)
    
    return Data


"""
Update the QUEUE
"""
async def create_queue(Data, payload, ):
    def keySort(key):
        stri = (int(len(Data['PlayerData'][key]['Proposal']['Supporters']) + int(len(Data['PlayerData'][key]['Proposal']['File']) > 1)) << 32 ) | ((1 << 32) - int(Data['PlayerData'][key]['Proposal']['DOB']))
        return stri


    # Sorted list of player IDs In order of Suporters, then Age
    sortedQ = list(sorted( dict(Data['PlayerData']).keys(), key=keySort))
    messages = [m async for m in payload['refs']['channels']['queue'].history(limit=200)]
    Data['Queue'] = sortedQ[::-1]


    # If Queue Structure not right size, regenerate to keep uniform spacing.
    if len(messages) != len(sortedQ): 
        for msg in messages: await msg.delete()
        messages == []
        for pid in sortedQ:  
            msg = await payload['refs']['channels']['queue'].send("Generating Proposal View")
            messages.append(msg)
            for r in ['👍', '👎', 'ℹ️']: await msg.add_reaction(r)
    messages = messages[::-1]


    # Update Messages with Stats
    for i in list(range(len(sortedQ))):
        pid     = sortedQ[i]
        player  = Data['PlayerData'][pid]['Name']
        msg     = messages[i]

        filename = f"{pid}-{Data['PlayerData'][pid]['Proposal']['DOB']}.txt"

        # Generate Message Content
        if Data['PlayerData'][pid]['Proposal']['File'] is None or len(Data['PlayerData'][pid]['Proposal']['File']) <= 1: 
            cont   = f"{player} Has No Proposal."
            files  = []
        else: 
            cont   = f"{player}'s Proposal: (Supporters: {len(Data['PlayerData'][pid]['Proposal']['Supporters'])})"
            files  = [discord.File(fp=io.StringIO(Data['PlayerData'][pid]['Proposal']['File']), filename=filename),]
        

        # Update Message Content
        if len(msg.attachments) != len(files) or (len(msg.attachments) != 0  and msg.attachments[0].filename != filename):
            await msg.edit( content = cont, attachments = files)
        elif msg.content != cont:  await msg.edit( content = cont)
        
        
       
        # Add MSG Badge
        if len(Data['PlayerData'][pid]['Proposal']['File']) <= 1:  
            if ('🥇' in list(map(str,msg.reactions))):  await msg.clear_reaction('🥇') #1st
            if ('🥈' in list(map(str,msg.reactions))):  await msg.clear_reaction('🥈') #1st
            if ('🥉' in list(map(str,msg.reactions))):  await msg.clear_reaction('🥉') #1st
            continue

        if len(Data['Queue']) <= 0: pass
        elif  (not '🥇' in list(map(str,msg.reactions))) and pid == Data['Queue'][0]:   await msg.add_reaction('🥇')
        elif      ('🥇' in list(map(str,msg.reactions))) and pid != Data['Queue'][0]:   await msg.clear_reaction('🥇') #1st
        
        if len(Data['Queue']) <= 1: pass
        elif  (not '🥈' in list(map(str,msg.reactions))) and pid == Data['Queue'][1]:   await msg.add_reaction('🥈')
        elif      ('🥈' in list(map(str,msg.reactions))) and pid != Data['Queue'][1]:   await msg.clear_reaction('🥈') #2st
        
        if len(Data['Queue']) <= 2: pass
        elif  (not '🥉' in list(map(str,msg.reactions))) and pid == Data['Queue'][2]:   await msg.add_reaction('🥉')
        elif      ('🥉' in list(map(str,msg.reactions))) and pid != Data['Queue'][2]:   await msg.clear_reaction('🥉') #3st
    print('..Queue Updated')
    return Data

"""
Setup Log Parameters and Channel List And Whatever You Need to Check on a Bot Reset.
Handles Change In Server Structure and the like. Probably Can Leave Alone.
"""
async def setup(Data,payload):
    if 'PlayerData' not in Data:
        Data['PlayerData'] = {}

    if 'Proposal#' not in Data:
        Data['Proposal#'] = 300

    if 'Turn' not in Data:
        Data['Turn'] = 0

    if 'Queue' not in Data:
        Data['Queue'] = {}

    if 'VotingEnabled' not in Data:
        Data['VotingEnabled'] = False

    if 'ProposingPlayer' not in Data:
        Data['ProposingPlayer'] = None

    if 'ProposingText' not in Data:
        Data['ProposingText'] = ""

    if 'ProposingMSGs' not in Data:
        Data['ProposingMSGs'] = []

    if 'CurrTurnStartTime' not in Data:
         Data['CurrTurnStartTime'] = 0

    if 'NextTurnStartTime' not in Data:
         Data['NextTurnStartTime'] = 0

    if 'Votes' not in Data:
         Data['Votes'] = {'Yay':[], 'Nay':[], 'Abstain':[], 'Proposal': {}}

    async for player in payload['refs']['server'].fetch_members(limit=1500):
        name = player.name + "#" + str(player.discriminator)
        pid = player.id
        if payload['refs']['roles']['Player'] not in player.roles: continue

        elif pid not in Data['PlayerData'] and name in Data['PlayerData']:
            Data['PlayerData'][pid] = dict(Data['PlayerData'][name])
            del Data['PlayerData'][name]

        elif pid not in Data['PlayerData'] and name not in Data['PlayerData']:
            Data['PlayerData'][pid] ={}

        if 'Name' not in  Data['PlayerData'][pid]:
            Data['PlayerData'][pid]['Name'] = name

        if 'Proposal' not in Data['PlayerData'][pid]:
            Data['PlayerData'][pid]['Proposal'] = {}

        if 'File'       not in Data['PlayerData'][pid]['Proposal']:
            Data['PlayerData'][pid]['Proposal']['File'] = ''

        if Data['PlayerData'][pid]['Proposal']['File'] is None:
            Data['PlayerData'][pid]['Proposal']['File'] = ''

        if 'Supporters' not in Data['PlayerData'][pid]['Proposal'] or type(Data['PlayerData'][pid]['Proposal']['Supporters']) is type(set()):
            Data['PlayerData'][pid]['Proposal']['Supporters'] = []

        if 'DOB'   not in Data['PlayerData'][pid]['Proposal']:
            Data['PlayerData'][pid]['Proposal']['DOB'] = now()

    for pid in dict(Data['PlayerData']):
        if 'Name' not in Data['PlayerData'][pid]:
            del Data['PlayerData'][pid]
            continue
        for propId in dict(Data['PlayerData']):
            Data['PlayerData'][propId]['Proposal']['Supporters'] = [pid if Data['PlayerData'][pid]['Name'] == x else x for x in Data['PlayerData'][propId]['Proposal']['Supporters']]


    print('Players In Game:',len(Data['PlayerData']))

    if clearOnStart:
        messages = [m async for m in payload['refs']['channels']['actions'].history(limit=200)]
        for msg in messages: await msg.delete()

        messages = [m async for m in payload['refs']['channels']['voting'].history(limit=200)]
        for msg in messages: await msg.delete()

        messages = [m async for m in payload['refs']['channels']['deck-edits'].history(limit=200)]
        for msg in messages: await msg.delete()

        messages = [m async for m in payload['refs']['channels']['proposals'].history(limit=200)]
        for msg in messages: await msg.delete()

    await create_queue(Data, payload)
    return await create_queue(Data, payload)
