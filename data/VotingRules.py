#
# Voting System Module For Discord Bot
################################
import pickle, sys, time, io, discord, datetime, urllib, re
tz = datetime.timezone.utc
"""
For a Custom Command !commandMe
"""
async def removeSupporter(Data, payload, *text):
    playerid, nth = payload['Content'].split(' ')[1:3]
    player = await getPlayer(playerid, payload)
    id = player.id
    nth = int(nth)
    print(f"Purging {nth} {Data['PlayerData'][id]['Proposal']['Supporters'][nth]} supporter for {player.name}")

    Data['PlayerData'][id]['Proposal']['Supporters'].pop(nth)
    return Data

async def tally(Data, payload, *text):
    await payload['raw'].channel.send(f"Current Vote Tally: {len(Data['Votes']['Yay'])} for, {len(Data['Votes']['Nay'])} against.")

async def extendTurn(Data, payload, *text):
    Data['VotePop'] += 24*60*60
    await payload['raw'].channel.send('Turn extended 24 hrs. Use !tick12 to manually trigger the next turn if needed')
    return Data

async def removeProposal(Data, payload, *text):
    playerid = payload['Content'].split(' ')[1]
    player = await getPlayer(playerid, payload)
    id = player.id
    print('Purging proposals for ',player.name)

    try:
        msg = await payload['refs']['channels']['queue'].fetch_message(Data['PlayerData'][id]['Proposal']['MSGID'])
        await msg.delete()
    except: pass
    Data['PlayerData'][id]['Proposal'] = {}
    Data['PlayerData'][id]['Proposal']['File'] = ''
    Data['PlayerData'][id]['Proposal']['Supporters'] = []
    Data['PlayerData'][id]['Proposal']['DOB'] = time.time()
    Data['PlayerData'][id]['Proposal']['MSGID'] = None

async def getPlayer(playerid, payload):
    if len(playerid) == 0:
        return None
    else:
        player = payload['refs']['server'].get_member(int(re.search(r'\d+', playerid).group()))
        if player is not None:
            #playerName = player.name + "#" + str(player.discriminator)
            return player
        else:
            await channel.send('Player with id, ' + playerid + ' cannot be found.')
    return None

async def tick12(Data, payload, *text):
    Data['VotePop'] = time.time()
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


async def popProposal(Data, payload, *text):
    print('PopP')
    if len(Data['Queue']) == 0: return Data

    playerprop = Data['Queue'].pop(0)
    msg = f"Proposal #{Data['Proposal#']}: \n\n "

    for line in Data['PlayerData'][playerprop]['Proposal']['File'].split('\n'):
        line += '\n'
        if len(msg + line) > 1950:
            await payload['refs']['channels']['voting'].send(msg)
            while len(line) > 1900:
                msgend = line[1900:].index(' ')
                await payload['refs']['channels']['voting'].send(line[:1900+msgend])
                line = line[1900+msgend:]
            msg = line
        else: msg += line

    if len(msg) > 0: await payload['refs']['channels']['voting'].send(msg)

    Data['Votes'] = {
    'Yay':[], #    Data['PlayerData'][playerprop]['Proposal']['Supporters'],
    'Nay':[],
    'Abstain':[],
    'Proposal': {
        Data['PlayerData'][playerprop]['Name'] : Data['PlayerData'][playerprop]['Proposal']['File']
    }}

    try:
        msg = await payload['refs']['channels']['queue'].fetch_message(Data['PlayerData'][playerprop]['Proposal']['MSGID'])
        await msg.delete()
    except: pass
    Data['PlayerData'][playerprop]['Proposal']['File'] = ''
    Data['PlayerData'][playerprop]['Proposal']['Supporters'] = []
    Data['PlayerData'][playerprop]['Proposal']['DOB'] = time.time()
    Data['PlayerData'][playerprop]['Proposal']['MSGID'] = None


    Data['Proposal#'] += 1
    await create_queue(Data, payload, force = True)



"""
Function Called on Reaction
"""
async def on_reaction(Data, payload):
    if payload['Channel'].name == 'voting':
        pass

    if payload['Channel'].name == 'queue' and payload['emoji'] == '👍' and payload['mode'] == 'add':
        author   = int(list(payload['Attachments'].keys())[0].split(".")[0])

        await payload['message'].remove_reaction('👍', payload['user'])
        if payload['user'].id not in Data['PlayerData'][author]['Proposal']['Supporters']:
            Data['PlayerData'][author]['Proposal']['Supporters'].append(payload['user'].id)
        await create_queue(Data, payload)

    if payload['Channel'].name == 'queue' and payload['emoji'] == '👎' and payload['mode'] == 'add':
        author   = int(list(payload['Attachments'].keys())[0].split(".")[0])
        await payload['message'].remove_reaction('👎', payload['user'])
        if payload['user'].id in Data['PlayerData'][author]['Proposal']['Supporters']:
            Data['PlayerData'][author]['Proposal']['Supporters'].remove(payload['user'].id)
        await create_queue(Data, payload)

    if payload['Channel'].name == 'queue' and payload['emoji'] == 'ℹ️' and payload['mode'] == 'add':
        author   = int(list(payload['Attachments'].keys())[0].split(".")[0])
        await payload['message'].remove_reaction('ℹ️', payload['user'])

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
        vote = payload['Content'].lower().strip()
        vote =    1* (vote in ['y', 'yes','yay', 'aye', 'pog']) \
                + 2* (vote in ['n', 'no', 'nay', 'sus']) \
                + 4* ('withdraw' in vote)

        if vote == 1:
            if payload['id'] not in Data['Votes']['Yay']:
                Data['Votes']['Yay'].append(payload['id'])
            if payload['id'] in Data['Votes']['Nay']:
                Data['Votes']['Nay'].remove( payload['id']  )
            if payload['id'] in Data['Votes']['Abstain']:
                Data['Votes']['Abstain'].remove( payload['id']  )
            await payload['raw'].add_reaction('✔️')
        elif vote == 2:
            if payload['id'] not in Data['Votes']['Nay']:
                Data['Votes']['Nay'].append(payload['id'])
            if payload['id'] in Data['Votes']['Yay']:
                Data['Votes']['Yay'].remove( payload['id']  )
            if payload['id'] in Data['Votes']['Abstain']:
                Data['Votes']['Abstain'].remove( payload['id']  )
            await payload['raw'].add_reaction('✔️')
        elif vote == 4:
            if payload['id'] not in Data['Votes']['Abstain']:
                Data['Votes']['Abstain'].append(payload['id'])
            if payload['Author'] in Data['Votes']['Yay']:
                Data['Votes']['Yay'].remove( payload['id']  )

            if payload['id'] in Data['Votes']['Nay']:
                Data['Votes']['Nay'].remove( payload['id']  )
            await payload['raw'].add_reaction('✔️')
        else:
            await payload['raw'].author.send( content = "Your vote is ambigious, Pleas use apropiate yay, nay, or withdraw" )
        #print(Data['Votes'])

    if payload['Channel'] == 'proposals':
        print('Saving Proposal')
        id = payload['id']
        print(payload['Attachments'].keys())
        if len(payload['Attachments']) == 1 and '.txt' in list(payload['Attachments'].keys())[0]:
            decoded = await list(payload['Attachments'].values())[0].read()
            decoded = decoded.decode(encoding="utf-8", errors="strict")
            Data['PlayerData'][id]['Proposal']['File'] = decoded

        if len(payload['Attachments']) == 0:
            Data['PlayerData'][id]['Proposal']['File'] = payload['Content']

        if Data['PlayerData'][id]['Proposal']['MSGID'] is not None:
            try: oldmsg = await payload['refs']['channels']['queue'].fetch_message(Data['PlayerData'][id]['Proposal']['MSGID'])
            except: oldmsg = None
            if oldmsg is not None: await oldmsg.delete()
            Data['PlayerData'][id]['Proposal']['MSGID'] = None

        if len(Data['PlayerData'][id]['Proposal']['File']) <= 1:
            await create_queue(Data, payload, force = True)
            return Data


        Data['PlayerData'][id]['Proposal']['DOB'] = time.time()
        Data['PlayerData'][id]['Proposal']['Supporters'] = []

        await create_queue(Data, payload, force = True)
    return Data

"""
Update Function Called Every 10 Seconds
"""
async def update(Data, payload):
    if (datetime.datetime.now(tz).hour - 5 == 0) and (time.time() - Data['VotePop'] > 61*60):
        await tick12(Data, payload)
    return Data
    #return await create_queue(Data, payload)


async def create_queue(Data, payload, force = False):
    sortedQ = list(sorted( dict(Data['PlayerData']).keys(),
                    key=lambda key: len(Data['PlayerData'][key]['Proposal']['Supporters'])-
                    1./(time.time() - Data['PlayerData'][key]['Proposal']['DOB']) +
                    int(len(Data['PlayerData'][key]['Proposal']['File']) > 1)
                     ))
    Data['Queue'] = sortedQ[::-1]

    for id in Data['PlayerData']:
        player = Data['PlayerData'][id]['Name']
        if Data['PlayerData'][id]['Proposal']['File'] is None or len(Data['PlayerData'][id]['Proposal']['File']) <= 1: continue
        if Data['PlayerData'][id]['Proposal']['MSGID'] is not None:
            try: msg = await payload['refs']['channels']['queue'].fetch_message(Data['PlayerData'][id]['Proposal']['MSGID'])
            except: msg = None
        else: msg = None

        cont = f"{player}'s Proposal: (Supporters: {len(Data['PlayerData'][id]['Proposal']['Supporters'])})"

        if msg is not None and msg.content != cont:
            await msg.edit( content = cont )

        elif msg is None:
            msg = await payload['refs']['channels']['queue'].send(
                cont,
                file=discord.File(fp=io.StringIO(Data['PlayerData'][id]['Proposal']['File']), filename=f"{id}.txt")
                )

            #Data['PlayerData'][id]['Proposal']['DOB'] = time.time()
            #Data['PlayerData'][id]['Proposal']['Supporters'] = []
            Data['PlayerData'][id]['Proposal']['MSGID'] = msg.id
            await msg.add_reaction('👍')
            await msg.add_reaction('👎')
            await msg.add_reaction('ℹ️')


        if  (not '🥇' in list(map(str,msg.reactions))) and id == Data['Queue'][0]:
            await msg.add_reaction('🥇')
            #await msg.pin()
        elif    ('🥇' in list(map(str,msg.reactions))) and id != Data['Queue'][0]:
            await msg.clear_reaction('🥇') #1st
            #if msg.pinned: await msg.unpin()

        if  (not '🥈' in list(map(str,msg.reactions))) and id == Data['Queue'][1]:
            await msg.add_reaction('🥈')
            #await msg.pin()
        elif    ('🥈' in list(map(str,msg.reactions))) and id != Data['Queue'][1]:
            await msg.clear_reaction('🥈') #2st
            #if msg.pinned: await msg.unpin()

        if  (not '🥉' in list(map(str,msg.reactions))) and id == Data['Queue'][2]:
            await msg.add_reaction('🥉')
            #await msg.pin()
        elif    ('🥉' in list(map(str,msg.reactions))) and id != Data['Queue'][2]:
            await msg.clear_reaction('🥉') #3st
            #if msg.pinned: await msg.unpin()


    #print('Queue',Data['Queue'])
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

    if 'VotePop' not in Data:
         Data['VotePop'] = 0

    if 'Votes' not in Data:
         Data['Votes'] = {'Yay':[], 'Nay':[], 'Abstain':[], 'Proposal': {}}

    async for player in payload['refs']['server'].fetch_members(limit=1500):
        name = player.name + "#" + str(player.discriminator)
        id = player.id
        if payload['refs']['roles']['Player'] not in player.roles: continue

        elif id not in Data['PlayerData'] and name in Data['PlayerData']:
            Data['PlayerData'][id] = dict(Data['PlayerData'][name])
            del Data['PlayerData'][name]

        elif id not in Data['PlayerData'] and name not in Data['PlayerData']:
            Data['PlayerData'][id] ={}

        if 'Name' not in  Data['PlayerData'][id]:
            Data['PlayerData'][id]['Name'] = name

        if 'Proposal' not in Data['PlayerData'][id]:
            Data['PlayerData'][id]['Proposal'] = {}

        if 'File'       not in Data['PlayerData'][id]['Proposal']:
            Data['PlayerData'][id]['Proposal']['File'] = ''

        if Data['PlayerData'][id]['Proposal']['File'] is None:
            Data['PlayerData'][id]['Proposal']['File'] = ''

        if 'Supporters' not in Data['PlayerData'][id]['Proposal'] or type(Data['PlayerData'][id]['Proposal']['Supporters']) is type(set()):
            Data['PlayerData'][id]['Proposal']['Supporters'] = []

        if 'Proposal'   not in Data['PlayerData'][id]['Proposal']:
            Data['PlayerData'][id]['Proposal']['DOB'] = time.time()

        if 'MSGID'   not in Data['PlayerData'][id]['Proposal']:
            Data['PlayerData'][id]['Proposal']['MSGID'] = None

    for id in dict(Data['PlayerData']):
        if 'Name' not in Data['PlayerData'][id]:
            del Data['PlayerData'][id]
            continue
        for propId in dict(Data['PlayerData']):
            Data['PlayerData'][propId]['Proposal']['Supporters'] = [id if Data['PlayerData'][id]['Name'] == x else x for x in Data['PlayerData'][propId]['Proposal']['Supporters']]


    print('Players In Game:',len(Data['PlayerData']))


    await create_queue(Data, payload)
    return await create_queue(Data, payload)
