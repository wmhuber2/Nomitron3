#
# Voting System Module For Discord Bot
################################
import pickle, sys, time, io, discord, datetime, urllib, re, random
tz = datetime.timezone.utc
"""
For a Custom Command !commandMe
"""



async def removeSupporter(Data, payload, *text):
    playerid, nth = payload['Content'].split(' ')[1:3]
    player = await getPlayer(playerid, payload)
    pid = player.id
    nth = int(nth)
    print(f"Purging {nth} {Data['PlayerData'][pid]['Proposal']['Supporters'][nth]} supporter for {player.name}")

    Data['PlayerData'][pid]['Proposal']['Supporters'].pop(nth)
    return Data

async def extendTurn(Data, payload, *text):
    Data['NextTurnStartTime'] += 24*60*60
    payload['raw'].channel.send('Turn extended 24 hrs. Use !tickTurn to manually trigger the next turn if needed')
    return Data

async def removeProposal(Data, payload, *text):
    playerid = payload['Content'].split(' ')[1]
    player = await getPlayer(playerid, payload)
    pid = player.id
    print('Purging proposals for ',player.name)

    try:
        msg = await payload['refs']['channels']['queue'].fetch_message(Data['PlayerData'][pid]['Proposal']['MSGID'])
        msg.delete()
    except: pass
    Data['PlayerData'][pid]['Proposal'] = {}
    Data['PlayerData'][pid]['Proposal']['File'] = ''
    Data['PlayerData'][pid]['Proposal']['Supporters'] = []
    Data['PlayerData'][pid]['Proposal']['DOB'] = time.time()

async def getPlayer(playerid, payload):
    if len(playerid) == 0: return None
    else:
        player = payload['refs']['server'].get_member(int(re.search(r'\d+', playerid).group()))
        if player is not None: return player
        else: channel.send('Player with id, ' + playerid + ' cannot be found.')
    return None

async def tickTurn(Data, payload, *text):
    if len(Data['Queue']) == 0:         Data['NextTurnStartTime'] = time.time() +     24 * 60 * 60
    else:                               Data['NextTurnStartTime'] = time.time() + 2 * 24 * 60 * 60
    
    Data['VotingEnabled'] = False
    await bot_tally(Data, payload)
    await popProposal(Data, payload)

async def setProp(Data, payload, *text):
    try: Data['Proposal#'] = int(text[0][1])
    except Exception as e: print(e)
    await payload['raw'].channel.send(f"Set Proposal to {Data['Proposal#']}")

async def bot_tally(Data, payload, *text):
    if len(Data['Votes']['Proposal']) != 1: return
    player, rule = list(Data['Votes']['Proposal'].items())[0]

    if len(Data['Votes']['Yay']) > len(Data['Votes']['Nay']):
        await payload['refs']['channels']['actions'].send(f"""{player}'s Proposal Passes
        Tally: {len(Data['Votes']['Yay'])} For, {len(Data['Votes']['Nay'])} Against.
        """)
    else:
        await payload['refs']['channels']['actions'].send(f"""{player}'s Proposal Failed
        Tally: {len(Data['Votes']['Yay'])} For, {len(Data['Votes']['Nay'])} Against.
        """)

def proposalText(Data):
    playerprop = Data['ProposingPlayer']

    msg = f"Proposal #{Data['Proposal#']}: "
    if Data['VotingEnabled']: msg += "**Status: Accepting Votes!** \n\n "
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
    for msg in await payload['refs']['channels']['voting'].pins(): msg.delete()
    playerprop = Data['Queue'].pop(0)
    for line in proposalText(Data):
        msg = await payload['refs']['channels']['voting'].send(line)
        msg.pin()

async def enableVoting(Data, payload):
    Data['VotingEnabled'] = True

async def popProposal(Data, payload, *text):
    print('PopP')

    for msg in await payload['refs']['channels']['voting'].pins(): msg.unpin()
    if len(Data['Queue']) == 0: return Data

    Data['ProposingPlayer'] = Data['Queue'].pop(0)
    Data['ProposingText']   = Data['ProposingText'][playerprop]['Proposal']['File']
    
    updateProposal(Data, payload, proposal)

    Data['Votes'] = {
    'Yay':[],
    'Nay':[],
    'Abstain':[],
    'Proposal': {
        Data['PlayerData'][playerprop]['Name'] : Data['PlayerData'][playerprop]['Proposal']['File']
    }}

    Data['PlayerData'][playerprop]['Proposal']['File'] = ''
    Data['PlayerData'][playerprop]['Proposal']['Supporters'] = []
    Data['PlayerData'][playerprop]['Proposal']['DOB'] = time.time()
    Data['PlayerData'][playerprop]['Proposal']['MSGID'] = None

    Data['Proposal#'] += 1
    await create_queue(Data, payload, )



"""
Function Called on Reaction
"""
async def on_reaction(Data, payload):
    if payload['Channel'].name == 'voting':
        pass

    if payload['Channel'].name == 'queue' and payload['mode'] == 'add':
        author   = int(list(payload['Attachments'].keys())[0].split(".")[0])
        payload['message'].remove_reaction(payload['emoji'] , payload['user'])
        
        if payload['emoji'] == '👍':
            if payload['user'].id not in Data['PlayerData'][author]['Proposal']['Supporters']:
                Data['PlayerData'][author]['Proposal']['Supporters'].append(payload['user'].id)
            await create_queue(Data, payload)

        if payload['emoji'] == '👎':
            if payload['user'].id in Data['PlayerData'][author]['Proposal']['Supporters']:
                Data['PlayerData'][author]['Proposal']['Supporters'].remove(payload['user'].id)
            await create_queue(Data, payload)

        if payload['emoji'] == 'ℹ️':
            msg =   f"------\n **{author}'s Proposal Info:**\n```Supporters:"
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
            if payload['Author ID'] not in Data['Votes']['Yay']:           Data['Votes']['Yay'].append(payload['Author ID'])
            if payload['Author ID'] in Data['Votes']['Nay']:               Data['Votes']['Nay'].remove( payload['Author ID']  )
            if payload['Author ID'] in Data['Votes']['Abstain']:           Data['Votes']['Abstain'].remove( payload['Author ID']  )
            payload['raw'].add_reaction('✔️')
        elif vote in ['nay', 'no', 'n']:
            if payload['Author ID'] not in Data['Votes']['Nay']:           Data['Votes']['Nay'].append(payload['Author ID'])
            if payload['Author ID'] in Data['Votes']['Yay']:               Data['Votes']['Yay'].remove( payload['Author ID']  )
            if payload['Author ID'] in Data['Votes']['Abstain']:           Data['Votes']['Abstain'].remove( payload['Author ID']  )
            payload['raw'].add_reaction('✔️')
        elif vote in ['abstain', 'withdraw']:
            if payload['Author ID'] not in Data['Votes']['Abstain']:       Data['Votes']['Abstain'].append(payload['Author ID'])
            if payload['Author'] in Data['Votes']['Yay']:                  Data['Votes']['Yay'].remove( payload['Author ID']  )
            if payload['Author ID'] in Data['Votes']['Nay']:               Data['Votes']['Nay'].remove( payload['Author ID']  )
            payload['raw'].add_reaction('✔️')
        else:
            payload['raw'].add_reaction('❌')
            payload['raw'].author.send( content = "Your vote is ambigious, Pleas use appropriate yay, nay, or withdraw text." )
        
    if payload['Channel'] == 'proposals':
        print('Saving Proposal')
        pid = payload['Author ID']
        if len(payload['Attachments']) == 1 and '.txt' in list(payload['Attachments'].keys())[0]:
            decoded = await list(payload['Attachments'].values())[0].read()
            decoded = decoded.decode(encoding="utf-8", errors="strict")
            Data['PlayerData'][pid]['Proposal']['File'] = decoded

        if len(payload['Attachments']) == 0:
            Data['PlayerData'][pid]['Proposal']['File'] = payload['Content']

        Data['PlayerData'][pid]['Proposal']['DOB'] = time.time()
        Data['PlayerData'][pid]['Proposal']['Supporters'] = []
        await create_queue(Data, payload, )


    if payload['Channel'] == 'deck-edits':
        print('Updating Proposal')
        if payload['Author ID'] != Data['ProposingPlayer'] or Data['VotingEnabled'] == False: 
            payload['refs']['channels']['queue'].send("The deck cannot be updated at this time in the turn.")
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
    if   (datetime.datetime.now(tz).hour == 0) and (time.time() - Data['NextTurnStartTime'] > 0):
        await tickTurn(Data, payload)
    elif (datetime.datetime.now(tz).hour == 0) and (time.time() - Data['CurrTurnStartTime'] > 24 * 60 * 60):
        await enableVoting(Data, payload)
    
    if (datetime.datetime.now(tz).hour != Data['Hour']):
        Data['Hour'] = datetime.datetime.now(tz).hour  - 5
    return Data


async def create_queue(Data, payload, ):
    def keySort(key):
        stri = (int(len(Data['PlayerData'][key]['Proposal']['Supporters']) + int(len(Data['PlayerData'][key]['Proposal']['File']) > 1)) << 32 ) | ((1 << 32) - int(Data['PlayerData'][key]['Proposal']['DOB']))
        return stri


    # Sorted list of player IDs In order of Suporters, then Age
    sortedQ = list(sorted( dict(Data['PlayerData']).keys(), key=keySort))
    messages = await payload['refs']['channels']['queue'].history(limit=200)
    Data['Queue'] = sortedQ[::-1]


    # If Queue Structure not right size, regenerate to keep uniform spacing.
    if len(messages) < len(sortedQ): 
        for msg in messages: msg.delete()
        for pid in sortedQ:  payload['refs']['channels']['queue'].send("Generating Proposal View")
    messages = await payload['refs']['channels']['queue'].history(limit=200)


    # Update Messages with Stats
    for i in range(len(sortedQ)):
        pid     = sortedQ[i]
        player  = Data['PlayerData'][pid]['Name']
        msg     = None
        if len(messages) <  i: msg     = messages[i]
        if len(messages) >= i: msg     = messages[i]

        # Generate Message Content
        if Data['PlayerData'][pid]['Proposal']['File'] is None or len(Data['PlayerData'][pid]['Proposal']['File']) <= 1: 
            cont   = f"{player} Has No Proposal."
        else: cont = f"{player}'s Proposal: (Supporters: {len(Data['PlayerData'][pid]['Proposal']['Supporters'])})"

        # Update Message Content
        if len(messages) <= i and messages[i].content != cont: 
            msg = messages[i]
            msg.edit( content = cont )
            await msg.remove_attachments(msg.attachments)
            msg.add_files([discord.File(fp=io.StringIO(Data['PlayerData'][pid]['Proposal']['File']), filename=f"{id}.txt")])
        else:
            msg = await payload['refs']['channels']['queue'].send( cont,
                file=discord.File(fp=io.StringIO(Data['PlayerData'][pid]['Proposal']['File']), filename=f"{id}.txt") )
            await msg.add_reaction('👍')
            await msg.add_reaction('👎')
            await msg.add_reaction('ℹ️')

        # Add MSG Badge
        if  (not '🥇' in list(map(str,msg.reactions))) and pid == Data['Queue'][0]:
            msg.add_reaction('🥇')
        elif    ('🥇' in list(map(str,msg.reactions))) and pid != Data['Queue'][0]:
            msg.clear_reaction('🥇') #1st
        if  (not '🥈' in list(map(str,msg.reactions))) and pid == Data['Queue'][1]:
            msg.add_reaction('🥈')
        elif    ('🥈' in list(map(str,msg.reactions))) and pid != Data['Queue'][1]:
            msg.clear_reaction('🥈') #2st
        if  (not '🥉' in list(map(str,msg.reactions))) and pid == Data['Queue'][2]:
            msg.add_reaction('🥉')
        elif    ('🥉' in list(map(str,msg.reactions))) and pid != Data['Queue'][2]:
            msg.clear_reaction('🥉') #3st

    print('Queue',Data['Queue'][:3])
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

    if 'Queue' not in Data:
        Data['Queue'] = {}

    if 'VotingEnabled' not in Data:
        Data['VotingEnabled'] = False

    if 'ProposingPlayer' not in Data:
        Data['ProposingPlayer'] = None

    if 'ProposingText' not in Data:
        Data['ProposingText'] = None

    if 'CurrTurnStartTime' not in Data:
         Data['CurrTurnStartTime'] = 0

    if 'CurrTurnStartTime' not in Data:
         Data['NextTurnStartTime'] = 0

    if 'Hour' not in Data:
         Data['Hour'] = -1

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
            Data['PlayerData'][pid]['Proposal']['DOB'] = time.time()

    for pid in dict(Data['PlayerData']):
        if 'Name' not in Data['PlayerData'][pid]:
            del Data['PlayerData'][pid]
            continue
        for propId in dict(Data['PlayerData']):
            Data['PlayerData'][propId]['Proposal']['Supporters'] = [pid if Data['PlayerData'][pid]['Name'] == x else x for x in Data['PlayerData'][propId]['Proposal']['Supporters']]


    print('Players In Game:',len(Data['PlayerData']))

    return await create_queue(Data, payload)
