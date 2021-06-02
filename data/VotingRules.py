#
# Voting System Module For Discord Bot
################################
import pickle, sys, time, io, discord, datetime, urllib, re
tz = datetime.timezone.utc
"""
For a Custom Command !commandMe
"""

async def purgeProposal(Data, payload, *text):
    playerid = payload['Content'].split(' ')[1]
    name = await getPlayer(playerid, payload)
    print('Purging proposals for ',name)

    Data['PlayerData'][name]['Proposal'] = {}
    Data['PlayerData'][name]['Proposal']['File'] = ''
    Data['PlayerData'][name]['Proposal']['Supporters'] = []
    Data['PlayerData'][name]['Proposal']['DOB'] = time.time()


async def getPlayer(playerid, payload):
    if len(playerid) == 0:
        return None
    else:
        player = payload['refs']['server'].get_member(int(re.search(r'\d+', playerid).group()))
        if player is not None:
            playerName = player.name + "#" + str(player.discriminator)
            return playerName
        else:
            await channel.send('Player with id, ' + playerid + ' cannot be found.')
    return None

async def tick12(Data, payload, *text):
    Data['VotePop'] = time.time()
    await tally(Data, payload)
    await popProposal(Data, payload)


async def setProp(Data, payload, *text):
    try: Data['Proposal#'] = int(text[0][1])
    except Exception as e: print(e)
    await payload['raw'].channel.send(f"Set Proposal to {Data['Proposal#']}")


async def tally(Data, payload, *text):
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
    print('PopP:', Data['Queue'])
    if len(Data['Queue']) == 0: return Data

    playerprop = Data['Queue'].pop(0)
    msg = f"Proposal #{Data['Proposal#']}: \n\n "

    for line in Data['PlayerData'][playerprop]['Proposal']['File'].split('\n'):
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
        playerprop : Data['PlayerData'][playerprop]['Proposal']['File']
    }}

    Data['PlayerData'][playerprop]['Proposal']['File'] = ''
    Data['PlayerData'][playerprop]['Proposal']['Supporters'] = []
    Data['PlayerData'][playerprop]['Proposal']['DOB'] = time.time()
    Data['Proposal#'] += 1
    await create_queue(Data, payload, force = True)



"""
Initiate New Player
"""
async def on_member_join(Data,player):
    name = player.name + "#" + str(player.discriminator)
    if payload['refs']['roles']['Player'] not in player.roles: return Data
    elif name not in Data['PlayerData']:
         Data['PlayerData'][name] = {}

    if 'Proposal' not in Data['PlayerData'][name]:
        Data['PlayerData'][name]['Proposal'] = {}


    if 'File'       not in Data['PlayerData'][name]['Proposal']:
        Data['PlayerData'][name]['Proposal']['File'] = ''

    if 'Supporters' not in Data['PlayerData'][name]['Proposal'] or type(Data['PlayerData'][name]['Proposal']['Supporters']) is type(set()):
        Data['PlayerData'][name]['Proposal']['Supporters'] = []

    if 'Proposal'   not in Data['PlayerData'][name]['Proposal']:
        Data['PlayerData'][name]['Proposal']['DOB'] = time.time()

    return Data

"""
Function Called on Reaction
"""
async def on_reaction(Data, payload):
    if payload['Channel'].name == 'voting':
        pass

    if payload['Channel'].name == 'queue' and payload['emoji'] == '👍' and payload['mode'] == 'add':
        author = payload['Content'].split("'s Proposal")[0]
        await payload['message'].remove_reaction('👍', payload['user'])
        if payload['name'] not in Data['PlayerData'][author]['Proposal']['Supporters']:
            Data['PlayerData'][author]['Proposal']['Supporters'].append(payload['name'])
        await create_queue(Data, payload)

    if payload['Channel'].name == 'queue' and payload['emoji'] == '👎' and payload['mode'] == 'add':
        author = payload['Content'].split("'s Proposal")[0]
        await payload['message'].remove_reaction('👎', payload['user'])
        if payload['name'] in Data['PlayerData'][author]['Proposal']['Supporters']:
            Data['PlayerData'][author]['Proposal']['Supporters'].remove(payload['name'])
        await create_queue(Data, payload)

    if payload['Channel'].name == 'queue' and payload['emoji'] == 'ℹ️' and payload['mode'] == 'add':
        author = payload['Content'].split("'s Proposal")[0]
        await payload['message'].remove_reaction('ℹ️', payload['user'])

        msg =   f"------\n **{author}'s Proposal Info:**\n```Supporters:"
        for p in Data['PlayerData'][author]['Proposal']['Supporters']: msg += '\n - ' + p
        msg += "```"
        await payload['user'].send(msg)

        msg = "**\nProposal:**\n"
        for line in Data['PlayerData'][author]['Proposal']['File'].split('\n'):
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
        vote =    1* (vote in ['y', 'yes','yay', 'aye']) \
                + 2* (vote in ['n', 'no', 'nay']) \
                + 4* ('withdraw' in vote)

        if vote == 1:
            if payload['Author'] not in Data['Votes']['Yay']:
                Data['Votes']['Yay'].append(payload['Author'])
            if payload['Author'] in Data['Votes']['Nay']:
                Data['Votes']['Nay'].remove( payload['Author']  )
            if payload['Author'] in Data['Votes']['Abstain']:
                Data['Votes']['Abstain'].remove( payload['Author']  )
            await payload['raw'].add_reaction('✔️')
        elif vote == 2:
            if payload['Author'] not in Data['Votes']['Nay']:
                Data['Votes']['Nay'].append(payload['Author'])
            if payload['Author'] in Data['Votes']['Yay']:
                Data['Votes']['Yay'].remove( payload['Author']  )
            if payload['Author'] in Data['Votes']['Abstain']:
                Data['Votes']['Abstain'].remove( payload['Author']  )
            await payload['raw'].add_reaction('✔️')
        elif vote == 4:
            if payload['Author'] not in Data['Votes']['Abstain']:
                Data['Votes']['Abstain'].append(payload['Author'])
            if payload['Author'] in Data['Votes']['Yay']:
                Data['Votes']['Yay'].remove( payload['Author']  )

            if payload['Author'] in Data['Votes']['Nay']:
                Data['Votes']['Nay'].remove( payload['Author']  )
            await payload['raw'].add_reaction('✔️')
        else:
            await payload['raw'].author.send( content = "Your vote is ambigious, Pleas use yay, nay, or withdraw" )
        print(Data['Votes'])

    if payload['Channel'] == 'proposals':
        print('Saving Proposal')
        player = payload['Author']
        print(payload['Attachments'].keys())
        if len(payload['Attachments']) == 1 and '.txt' in list(payload['Attachments'].keys())[0]:
            decoded = await list(payload['Attachments'].values())[0].read()
            decoded = decoded.decode(encoding="utf-8", errors="strict")
            Data['PlayerData'][player]['Proposal']['File'] = decoded

        if len(payload['Attachments']) == 0:
            Data['PlayerData'][player]['Proposal']['File'] = payload['Content']

        if Data['PlayerData'][player]['Proposal']['MSGID'] is not None:
            try: oldmsg = await payload['refs']['channels']['queue'].fetch_message(Data['PlayerData'][player]['Proposal']['MSGID'])
            except: oldmsg = None
            if oldmsg is not None: await oldmsg.delete()
            Data['PlayerData'][player]['Proposal']['MSGID'] = None
        if len(Data['PlayerData'][player]['Proposal']['File']) <= 1: return

        msg = await payload['refs']['channels']['queue'].send(
            f"{player}'s Proposal: (Supporters: {len(Data['PlayerData'][player]['Proposal']['Supporters'])})",
            file=discord.File(fp=io.StringIO(Data['PlayerData'][player]['Proposal']['File']), filename=f"{player}'s Proposal.txt'")
            )

        Data['PlayerData'][player]['Proposal']['DOB'] = time.time()
        Data['PlayerData'][player]['Proposal']['Supporters'] = []
        Data['PlayerData'][player]['Proposal']['MSGID'] = msg.id
        await msg.add_reaction('👍')
        await msg.add_reaction('👎')
        await msg.add_reaction('ℹ️')

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

    pasmessages = list(await payload['refs']['channels']['queue'].history(limit=100).flatten())[::-1]
    for player in Data['PlayerData']:

        if Data['PlayerData'][player]['Proposal']['File'] is None or len(Data['PlayerData'][player]['Proposal']['File']) <= 1: continue
        if Data['PlayerData'][player]['Proposal']['MSGID'] is not None:
            try: msg = await payload['refs']['channels']['queue'].fetch_message(Data['PlayerData'][player]['Proposal']['MSGID'])
            except: msg = None
        else: msg = None

        cont = f"{player}'s Proposal: (Supporters: {len(Data['PlayerData'][player]['Proposal']['Supporters'])})"
        if msg is not None and msg.content != cont:
            await msg.edit( content = cont )

        elif msg is None:
            msg = await payload['refs']['channels']['queue'].send(
                cont,
                file=discord.File(fp=io.StringIO(Data['PlayerData'][player]['Proposal']['File']), filename=f"{player}'s Proposal.txt'")
                )

            Data['PlayerData'][player]['Proposal']['DOB'] = time.time()
            Data['PlayerData'][player]['Proposal']['Supporters'] = []
            Data['PlayerData'][player]['Proposal']['MSGID'] = msg.id
            await msg.add_reaction('👍')
            await msg.add_reaction('👎')
            await msg.add_reaction('ℹ️')


        if  (not '🥇' in list(map(str,msg.reactions))) and player == Data['Queue'][0]:
            await msg.add_reaction('🥇')
            #await msg.pin()
        elif    ('🥇' in list(map(str,msg.reactions))):
            await msg.clear_reaction('🥇') #1st
            #if msg.pinned: await msg.unpin()

        if  (not '🥈' in list(map(str,msg.reactions))) and player == Data['Queue'][1]:
            await msg.add_reaction('🥈')
            #await msg.pin()
        elif    ('🥈' in list(map(str,msg.reactions))):
            await msg.clear_reaction('🥈') #2st
            #if msg.pinned: await msg.unpin()

        if  (not '🥉' in list(map(str,msg.reactions))) and player == Data['Queue'][2]:
            await msg.add_reaction('🥉')
            #await msg.pin()
        elif    ('🥉' in list(map(str,msg.reactions))):
            await msg.clear_reaction('🥉') #3st
            #if msg.pinned: await msg.unpin()


    print('Queue',Data['Queue'])
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
        if payload['refs']['roles']['Player'] not in player.roles: continue
        elif name not in Data['PlayerData']:
             Data['PlayerData'][name] = {}

        if 'Proposal' not in Data['PlayerData'][name]:
            Data['PlayerData'][name]['Proposal'] = {}

        if 'File'       not in Data['PlayerData'][name]['Proposal']:
            Data['PlayerData'][name]['Proposal']['File'] = ''

        if Data['PlayerData'][name]['Proposal']['File'] is None:
            Data['PlayerData'][name]['Proposal']['File'] = ''

        if 'Supporters' not in Data['PlayerData'][name]['Proposal'] or type(Data['PlayerData'][name]['Proposal']['Supporters']) is type(set()):
            Data['PlayerData'][name]['Proposal']['Supporters'] = []

        if 'Proposal'   not in Data['PlayerData'][name]['Proposal']:
            Data['PlayerData'][name]['Proposal']['DOB'] = time.time()

        if 'MSGID'   not in Data['PlayerData'][name]['Proposal']:
            Data['PlayerData'][name]['Proposal']['MSGID'] = None

    await create_queue(Data, payload)
    return await create_queue(Data, payload)
