#
# Voting System Module For Discord Bot
################################
import pickle, sys, time, io, discord, datetime, urllib, re, random
tz = datetime.timezone.utc
"""
For a Custom Command !commandMe
"""


admins = ['Fenris#6136', 'Crorem#6962', 'iann39#8298', 'Alekosen#6969', None]
zipChan = list(zip(['Votes','Suber-Votes-1','Suber-Votes-2', 'Suber-Votes-3', 'Suber-Votes-4'],  ['voting', 'voting-1','voting-2','voting-3','voting-4',]))
    

last_update_prop_time = 0
hold_for_update_prop = False

last_update_deck_time = 0
hold_for_update_deck = False

whipEmojiMap = "1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣ 9️⃣ 🔟".split(' ')
endorseEmojiMap = ['👍', '👎', 'ℹ️']

zeroday = 1641016800 # Jan 1 2022
day  = 60 * 60 * 24

def now(): return time.time() - zeroday

def getTime(t):
    day =  t// (24*3600)

    sc  = int((t % (60  )    ) // (1      ))
    mn  = int((t % (60*60)   ) // (60     ))
    hr  = int((t % (24*60*60)) // (60*60  ))
    day = int((t             ) // (24*3600))
    return f"{day} @ {hr}:{mn} {sc}s"

async def turnStats(Data, payload, *text):
    propPlayer = Data['Votes']['ProposingPlayer']
    if propPlayer not in ["DOOM", None]: 
        propPlayer = Data['PlayerData'][ Data['Votes']['ProposingPlayer'] ]['Name']

    msg = f"**Turn Stats:**```\n"
    msg += f"Proposal#            :   {Data['Proposal#']}\n"
    msg += f"Voting Enabled       :   {Data['VotingEnabled']}\n"
    msg += f"Proposing Player     :   {propPlayer}\n"
    msg += f"Curr Turn Start Time :   {getTime(Data['CurrTurnStartTime'])}\n"
    msg += f"Next Turn Start Time :   {getTime(Data['NextTurnStartTime'])}\n"
    msg += f"Time Now             :   {getTime(now())}\n"
    msg += f"Time Elapsed         :   {getTime(now() - Data['CurrTurnStartTime'])}\n"
    msg += f"Time Remaining       :   {getTime(Data['NextTurnStartTime'] - now())}\n"
    msg += f"Votes                :   {Data['Votes']}\n```"
    await payload['raw'].channel.send(msg)

async def create_array(Data, payload, ):
    def keySort(key): return int(Data['Subers'][key]['Proposal#']) 
    
    def keySortSub(key):
        return (int(len(Data['Subers'][suberKey]['Assenter']['Supporters'])) << 32 ) | ((1 << 32) - int(Data['Subers'][suberKey]['Assenter']['DOB'])) 

    # Sorted list of player IDs In order of Proposal Parent
    sortedArrays = list(sorted( dict(Data['Subers']).keys(), key=keySort))
    messages = [m async for m in payload['refs']['channels']['array'].history(limit=100)]
    


    # If Array Length not right size, regenerate to keep uniform spacing.
    if len(messages) != 12 : 
        await payload['refs']['channels']['array'].purge()
        messages = []
        for pid in range(12):  
            msg = await payload['refs']['channels']['array'].send("Empty SUBER")
            messages.append(msg)


    # Update Messages with Stats
    for i in list(range(len(sortedArrays))):
        suberKey  = sortedArrays[i]

        arrayMajorMinors = list(sorted( ('Assenter', 'Dissenter'), key=keySortSub))
        indexMajorMinors = 0
        for MajorOrMinor in arrayMajorMinors:               
            msg      = messages[i*2 + indexMajorMinors]
            indexMajorMinors += 1
            # Generate Message Content

            # Whip Nominate Phase
            cont = ""
            files  = []

            if Data['Subers'][suberKey][MajorOrMinor]['Is Official']:

                filename = f"0-{suberKey}-{MajorOrMinor}-{Data['Subers'][suberKey][MajorOrMinor]['DOB']}.txt"
                player = Data['PlayerData'][Data['Subers'][suberKey][MajorOrMinor]['Whip']]['Name']

                if Data['Subers'][suberKey][MajorOrMinor]['Proposal'] is None or len(Data['Subers'][suberKey][MajorOrMinor]['Proposal']) <= 1: 
                    cont   = f"**Proposal {suberKey}'s {MajorOrMinor} SUBER:** Suber {Data['Subers'][suberKey][MajorOrMinor]['Party']} Whip:" \
                             f"{player} Has No Proposal."
                    files  = []
                else: 
                    cont   = f"**Proposal {suberKey}'s {MajorOrMinor} SUBER:** Suber {Data['Subers'][suberKey][MajorOrMinor]['Party']} Whip:" \
                             f"{player} (Supporters: {len(Data['Subers'][suberKey][MajorOrMinor]['Supporters'])})"
                    files  = [discord.File(fp=io.StringIO(Data['Subers'][suberKey][MajorOrMinor]['Proposal']), filename=filename),]
                
                for e in whipEmojiMap: 
                    for r in msg.reactions:
                        if str(r) == e: await msg.remove_reaction(e , msg.author)
                for e in endorseEmojiMap: 
                    hasEmoji = False
                    for r in msg.reactions:
                        if str(r) == e: hasEmoji = True
                    if not hasEmoji: await msg.add_reaction(e)
                for r in msg.reactions:
                    if str(r) == '🎗️': await msg.remove_reaction('🎗️' , msg.author)
            else:

                filename = f"0-{suberKey}-{MajorOrMinor}-{Data['Subers'][suberKey]['Date']}.txt"
                if len(Data['Subers'][suberKey][MajorOrMinor]['Whip']) == 0:
                    cont = f"**Proposal {suberKey}'s {MajorOrMinor} SUBER:** Vote for a WHIP by reacting to denote an Affirmative Vote\n" \
                           f"   WHIPs can nominate themselves by clicking 🎗️ \n\n No Whips Have Nominated Themselves." 
                    SupportRecord = "Whips Nominee Support Record:\n\n No Whips Have Nominated Themselves."

                    filename = str(abs(hash(SupportRecord)) % (10 ** 8)) + filename
                    files  = [discord.File(fp=io.StringIO(SupportRecord), filename=filename)]

                else:
                    cont  = f"**Proposal {suberKey}'s {MajorOrMinor} SUBER:** Vote for a WHIP by reacting to denote an Affirmative Vote\n" \
                            f"   WHIPs can nominate themselves by clicking 🎗️\n\nWhip Nominees:"
                    for i in range(len(Data['Subers'][suberKey][MajorOrMinor]['Whip'])):
                        cont += f"\n {whipEmojiMap[i]} : "
                        cont += f"{Data['PlayerData'][Data['Subers'][suberKey][MajorOrMinor]['Whip'][i]['Name']]['Name']}"
                            
                    
                    # Generate Support Record
                    SupportRecord = "Whips Nominee Support Record:\n\n"
                    for i in range(len(Data['Subers'][suberKey][MajorOrMinor]['Whip'])):
                        whip = Data['Subers'][suberKey][MajorOrMinor]['Whip'][i]['Name']
                        s = f"\n{Data['PlayerData'][whip]['Name']} Supporters:\n"
                        for sup in Data['Subers'][suberKey][MajorOrMinor]['Whip'][i]['Supporters']:
                            s += f"   -{Data['PlayerData'][sup]['Name']}\n"
                        SupportRecord += s

                    filename = str(abs(hash(SupportRecord)) % (10 ** 8)) + filename
                    files  = [discord.File(fp=io.StringIO(SupportRecord), filename=filename)]
                    
                
                hasEmoji = False
                for r in msg.reactions:
                    if str(r) == '🎗️': hasEmoji = True
                if not hasEmoji: await msg.add_reaction('🎗️')
                
                for e in whipEmojiMap[len(Data['Subers'][suberKey][MajorOrMinor]['Whip']):]: 
                    for r in msg.reactions:
                        if str(r) == e: await msg.remove_reaction(e , msg.author)
                for e in whipEmojiMap[:len(Data['Subers'][suberKey][MajorOrMinor]['Whip'])]: 
                    hasEmoji = False
                    for r in msg.reactions:
                        if str(r) == e: hasEmoji = True
                    if not hasEmoji: await msg.add_reaction(e)

                for e in endorseEmojiMap: 
                    for r in msg.reactions:
                        if str(r) == e: await msg.remove_reaction(e , msg.author)

            # Update Message Content
            if len(msg.attachments) != len(files) or (len(msg.attachments) != 0  and msg.attachments[0].filename != filename):
                await msg.edit( content = cont, attachments = files)
            elif msg.content != cont:  
                await msg.edit( content = cont, attachments = files)
            Data['Subers'][suberKey][MajorOrMinor]['msgid'] = msg.id
    
    for msg in messages[len(sortedArrays)*2:]:
        if msg.content != "Empty Suber":  
            await msg.edit(content = "Empty Suber", attachments = [])
        if len(msg.reactions) > 0:
            for r in msg.reactions: await msg.remove_reaction(r , msg.author)

    print('..Array Updated')
    Data['Array'] = sortedArrays[::-1]
    return Data

async def extendTurn(Data, payload, *text):
    if payload.get('Author') not in admins: return

    Data['NextTurnStartTime'] += day
    await payload['raw'].channel.send('Turn extended 24 hrs. Use !tickTurn to manually trigger the next turn if needed')
    return Data

async def reduceTurn(Data, payload, *text):
    if payload.get('Author') not in admins: return

    Data['NextTurnStartTime'] -= day
    await payload['raw'].channel.send('Turn reduced by 24 hrs. Use !tickTurn to manually trigger the next turn if needed')
    return Data

async def togglePermInactive(Data, payload, *text):
    if payload.get('Author') not in admins: return 

    playerid = payload['Content'].split(' ')[1]
    player = await getPlayer(playerid, payload)
    pid = player.id

    isInactive = payload['refs']['players'][pid].get_role(payload['refs']['roles']['Inactive'].id) is not None

    if isInactive:
        await payload['refs']['players'][pid].remove_roles(payload['refs']['roles']['Inactive'])
        Data['PlayerData'][pid]['Inactive'] = None

    else:
        await payload['refs']['players'][pid].add_roles(payload['refs']['roles']['Inactive'])
        Data['PlayerData'][pid]['Inactive'] = "Perm"

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
        else: await payload['raw'].channel.send('Player with id, ' + playerid + ' cannot be found.')
    return None

async def tickTurn(Data, payload, *text):
    if payload.get('Author') not in admins: return

    print('.Turn Ticking')
    Data['CurrTurnStartTime'] = (now()//day) * day
    Data['VotingEnabled'] = False
    Data['Turn'] += 1

    await bot_tally(Data, payload)
    await popProposal(Data, payload)
    await suberTick(Data, payload)

    if len(Data['Votes']['ProposingText']) < 1:  Data['NextTurnStartTime'] = (now()//day  + 1) * day
    else:                                        Data['NextTurnStartTime'] = (now()//day  + 2) * day

async def suberTick(Data, payload):
    def keySortSub(arr):
        return len(arr['Supporters'])
    
    for suberKey in list(Data['Subers'].keys()): 
        minority = Data['Subers'][suberKey]['Loser']

        # Tally Whip Votes
        if Data['Subers'][suberKey]['Turn'] +1 <= Data['Turn']:

            majority = ['Assenter', 'Dissenter']
            majority.remove(minority)
            majority = majority[0]


            # Not Loser Tally
            if not Data['Subers'][suberKey][majority]['Is Official']:
                # Set Whip Majority

                arrayMajorMinors = list(Data['Subers'][suberKey][majority]['Whip'])
                arrayMajorMinors.sort(key=keySortSub)
                print(arrayMajorMinors)
                if len(arrayMajorMinors) > 0 and Data['Subers'][suberKey][minority]['Is Official'] and \
                len(arrayMajorMinors[0]['Supporters']) >  len(Data['Subers'][suberKey][majority]["Members"])*0.5 and \
                (len(arrayMajorMinors) == 1 or len(arrayMajorMinors[0]['Supporters']) != len(arrayMajorMinors[1]['Supporters'])):
                    Data['Subers'][suberKey][majority]['Whip'] = arrayMajorMinors[0]['Name']
                    Data['Subers'][suberKey][majority]['Is Official'] = True
                    cont = f"Proposal {suberKey}'s SUBER: {Data['PlayerData'][arrayMajorMinors[0]['Name']]['Name']} has been elected as a Whip." 
                    await payload['refs']['channels']['actions'].send(cont)


            # Loser Tally
            if not Data['Subers'][suberKey][minority]['Is Official']:
                arrayMajorMinors = list(sorted( Data['Subers'][suberKey][minority]['Whip'], key=keySortSub))

                # If No Whip Consensis Vote
                if len(arrayMajorMinors) == 0 or (len(arrayMajorMinors) != 1 and \
                len(arrayMajorMinors[0]['Supporters']) <=  len(Data['Subers'][suberKey][minority]['Members'])*0.5 and \
                len(arrayMajorMinors[0]['Supporters']) == len(arrayMajorMinors[1]['Supporters'])):
                    cont = f"Proposal {suberKey}'s SUBER: Disbanded Due To Failed Majority Vote of Minority Whip" 
                    await payload['refs']['channels']['actions'].send(cont)
                    del Data['Subers'][suberKey]
                    continue

                # Set Whip Minority
                else:
                    Data['Subers'][suberKey][minority]['Whip'] = arrayMajorMinors[0]['Name']
                    Data['Subers'][suberKey][minority]['Is Official'] = True
                    cont = f"Proposal {suberKey}'s SUBER: {Data['PlayerData'][arrayMajorMinors[0]['Name']]['Name']} has been elected as a Whip." 
                    await payload['refs']['channels']['actions'].send(cont)
                

        # Week Expiration Test
        if (now() - Data['Subers'][suberKey]['Date']) > 7 * day:
            cont = f"Proposal {suberKey}'s SUBER's Week Expiration Reached. Suber is Disbanded " 
            await payload['refs']['channels']['actions'].send(cont)
            del Data['Subers'][suberKey]

    await create_array(Data, payload, )
   
async def setProp(Data, payload, *text):
    if payload.get('Author') not in admins: return
    try: Data['Proposal#'] = int(text[0][1])
    except Exception as e: print(e)
    await payload['raw'].channel.send(f"Set Proposal to {Data['Proposal#']}")

async def bot_tally(Data, payload, *text):
    if payload.get('Author') not in admins: return 

    # Tally Main Voting Queue
    if Data['Votes']['ProposingPlayer'] is None or len(Data['Votes']['ProposingText']) <= 1:
            await payload['refs']['channels']['actions'].send(f"**End of Turn #{Data['Turn']}.** No Proposal was on Deck")
    else:
        player = "Undefined"
        isDoom = 0
        if Data['Votes']['ProposingPlayer'] == "DOOM":
            player = "Intentional Game Design"
            isDoom = 1
        else:
            player = Data['PlayerData'][ Data['Votes']['ProposingPlayer'] ]['Name']

        votingPlayers  = len(Data['Votes']['Yay']) + len(Data['Votes']['Nay'])
        activePlayers = len(payload['refs']['roles']['Player'].members) - len(payload['refs']['roles']['Inactive'].members)
        losers        = None


        # Tally Main Voting Queue
        if len(Data['Votes']['ProposingText']) <= 1:
            await payload['refs']['channels']['actions'].send(f"**End of Turn #{Data['Turn']}.** No Proposal was on Deck\n\n" )
        elif len(Data['Votes']['Yay']) + isDoom > len(Data['Votes']['Nay']):
            losers = ['Dissenter','Nay']
            await payload['refs']['channels']['actions'].send(f"**End of Turn #{Data['Turn']}.** {player}'s Proposal Passes\n" \
                f"- Tally: {len(Data['Votes']['Yay'])} For, {len(Data['Votes']['Nay'])} Against.")
        else:
            losers = ['Assenter','Yay']
            await payload['refs']['channels']['actions'].send(f"**End of Turn #{Data['Turn']}.** {player}'s Proposal Failed \n" \
                f"- Tally: {len(Data['Votes']['Yay'])} For, {len(Data['Votes']['Nay'])} Against.")
            for line in proposalText(Data, 'Votes'):
                await payload['refs']['channels']['failed-proposals'].send(line)
        


        # Form SUBERS if necassary
        print(len(Data['Votes'][losers[1]]) , votingPlayers, activePlayers)
        if len(Data['Votes'][losers[1]])  > 0.2 * votingPlayers and (activePlayers < 2 * votingPlayers):
            Data['Subers'][Data['Votes']['Proposal#']] = {
                'Proposal#' : Data['Votes']['Proposal#'],
                'Assenter': {
                    'Members':Data['Votes']['Yay'], 'Is Official': False, 'Whip' : [],
                    'Proposal' : "", 'Supporters' : [],'DOB' : now(),
                    'Party': ['Minority', 'Majority'][losers == "Yay"]
                },
                'Dissenter': {
                    'Members':Data['Votes']['Nay'], 'Is Official': False, 'Whip' : [],
                    'Proposal' : "", 'Supporters' : [], 'DOB' : now(),
                    'Party': ['Minority', 'Majority'][losers == "Nay"]
                },
                'Date': now(), 'Turn': Data['Turn'], 'Voting Channel': None, 'Loser' : losers[0]
            }
            await payload['refs']['channels']['actions'].send(f"**A SUBER has been formed! \n" \
            f"   Assenters: {' '.join([f'<@{pid}>' for pid in Data['Subers'][Data['Votes']['Proposal#']]['Assenter']['Members']])}\n\n" \
            f"   Dissenters: {' '.join([f'<@{pid}>' for pid in Data['Subers'][Data['Votes']['Proposal#']]['Dissenter']['Members']])}\n\n")


    # Tally SUBERS
    for chan in ['Suber-Votes-1','Suber-Votes-2', 'Suber-Votes-3', 'Suber-Votes-4']: 
        if Data[chan]['ProposingPlayer'] is None: continue
        player        = Data['PlayerData'][ Data[chan]['ProposingPlayer'] ]['Name']
        votingPlayers  = len(Data[chan]['Yay']) + len(Data[chan]['Nay'])
        activePlayers = len(payload['refs']['roles']['Player'].members) - len(payload['refs']['roles']['Inactive'].members)

        if len(Data[chan]['ProposingText']) < 1: continue
        if len(Data[chan]['Yay']) > len(Data[chan]['Nay']):
            await payload['refs']['channels']['actions'].send(f" - {player}'s SUBER Proposal Passes\n" \
                f"- Tally: {len(Data[chan]['Yay'])} For, {len(Data[chan]['Nay'])} Against.\nSUBER is Disbanded\n\n")
            del Data['Subers'][Data[chan]['SuberKey']]

        else:
            await payload['refs']['channels']['actions'].send(f" - {player}'s SUBER Proposal Failed \n" \
                f"- Tally: {len(Data[chan]['Yay'])} For, {len(Data[chan]['Nay'])} Against.\n\n")
            for line in proposalText(Data, chan):
                await payload['refs']['channels']['failed-proposals'].send(line)

    await payload['refs']['channels']['actions'].send(f"**Start Of Turn #{Data['Turn']+1}. **")

        
def proposalText(Data, voteChan):
    playerprop = Data[voteChan]['ProposingPlayer']
    if playerprop is None: return []

    msg = f"Proposal #{Data[voteChan]['Proposal#']}: "
    if voteChan != 'Votes': msg += Data[voteChan]['Suber']
    if Data['VotingEnabled'] or voteChan != 'Votes': msg += f"**Status: ({len(Data[voteChan]['Yay'])} For, {len(Data[voteChan]['Nay'])} Against.)** \n\n "
    else                    : msg += "**Status: ON DECK (No Voting)** \n\n "
    topin = []

    for line in Data[voteChan]['ProposingText'].split('\n'):
        line += '\n'
        if len(msg + line) > 1920:
            topin.append(msg)
            msg = ""

            for word in line.split(' '):
                if len(msg + word) > 1920:
                    topin.append(msg)
                    msg = str(word)
                else: msg += word
                msg += " "
        else: msg += line
    if len(msg) > 1: topin.append(msg)
    return topin

async def updateProposal(Data, payload):
    if last_update_prop_time +5 < time.time():
        await actuallyUpdateVotingProposal(Data, payload)
    else:
        hold_for_update_prop = True

async def actuallyUpdateVotingProposal(Data, payload):
    def is_proposalMSG(m): 
        for chan in ['Votes','Suber-Votes-1','Suber-Votes-2', 'Suber-Votes-3', 'Suber-Votes-4']:
            if m.id in Data[chan]['ProposingMSGs']: return True
        return False

    last_update_prop_time = time.time()
    hold_for_update_prop = False
    
    for subChan, disChan in zipChan:
        if Data['VotingEnabled'] or subChan != 'Votes':
            lines = proposalText(Data, subChan)
            if len(lines) != len(Data[subChan]['ProposingMSGs']):
                for msg in Data[subChan]['ProposingMSGs']: await msg.delete()
                Data[subChan]['ProposingMSGs'] = []
                for line in lines:
                    msg = await payload['refs']['channels'][disChan].send(line)
                    Data[subChan]['ProposingMSGs'].append(msg.id)
            for i in range(len(Data[subChan]['ProposingMSGs'])): 
                mid  = Data[subChan]['ProposingMSGs'][i] 
                line = lines[i]
                try: msg = await payload['refs']['channels'][disChan].fetch_message(mid) 
                except: 
                    Data[subChan]['ProposingMSGs'] = []
                    await actuallyUpdateVotingProposal(Data, payload)
                    return
                await msg.edit(content = line)
        else:
            await payload['refs']['channels'][disChan].purge(limit=100, check=is_proposalMSG)
            Data[subChan]['ProposingMSGs'] = []
            for line in proposalText(Data, subChan):
                msg = await payload['refs']['channels'][disChan].send(line)
                Data[subChan]['ProposingMSGs'].append(msg.id)

async def enableVoting(Data, payload, *text):
    if payload.get('Author') not in admins: return
    print('..Enabling Voting')
    Data['VotingEnabled'] = True

    await payload['refs']['channels']['voting'].set_permissions(payload['refs']['roles']['Player'], send_messages=True)
    await payload['refs']['channels']['actions'].send("Players May Now Vote in #voting.")
    for p in payload['refs']['players'].values(): await p.remove_roles(payload['refs']['roles']['On Deck'])
    await updateProposal(Data, payload)

async def popProposal(Data, payload, *text):
    if payload.get('Author') not in admins: return
    def keySortSub(key):
        return (int(len(Data['Subers'][suberKey]['Assenter']['Supporters'])) << 32 ) | ((1 << 32) - int(Data['Subers'][suberKey]['Assenter']['DOB'])) 

    # Reset Channels
    for subChan, disChan in list(zipChan): 
        if disChan == 'voting': Data[subChan]['Suber'] = None
        Data[subChan]['ProposingPlayer'] = None
        Data[subChan]['ProposingMSGs']   = []
        Data[subChan]['ProposingText']   = ""
        await payload['refs']['channels'][disChan].set_permissions(payload['refs']['roles']['Player'], send_messages=False)


    # Voting Channel
    print('..PopProposal To Deck:')
    gotProp = False
    if len(Data['Queue']) > 0: 
        pid = Data['Queue'].pop(0)
        print('...',pid, Data['PlayerData'][pid]['Name'])
        if len(Data['PlayerData'][pid]['Proposal']['File']) > 1: 
            for p in payload['refs']['players'].values(): await p.remove_roles(payload['refs']['roles']['On Deck'])
            await payload['refs']['players'][pid].add_roles(payload['refs']['roles']['On Deck'])
            
            Data['Votes'] = { 'Yay':[], 'Nay':[], 'Abstain':[], 'ProposingMSGs':[], 'ProposingPlayer':pid,
                            'ProposingText':str(Data['PlayerData'][pid]['Proposal']['File']),
                            'Proposal#':Data['Proposal#']}
            Data['Proposal#']       += 1
            Data['PlayerData'][pid]['Proposal']['File'] = ''
            Data['PlayerData'][pid]['Proposal']['Supporters'] = []
            Data['PlayerData'][pid]['Proposal']['DOB'] = now()
            gotProp = True
    if not gotProp:
        Data['Votes'] = { 'Yay':[], 'Nay':[], 'Abstain':[], 'ProposingMSGs':[], 'ProposingPlayer':"DOOM",
                            'ProposingText':str("A Doom Proposal Shall Be Determined By Mods"),
                            'Proposal#':Data['Proposal#']}
        Data['Proposal#']       += 1
        Data['PlayerData'][pid]['Proposal']['File'] = ''
        Data['PlayerData'][pid]['Proposal']['Supporters'] = []
        Data['PlayerData'][pid]['Proposal']['DOB'] = now()



    # Suber Channels
    for suberKey in Data['Subers'].keys(): 
        MajorOrMinor = list(sorted( ['Assenter', 'Dissenter'], key=keySortSub))[0]
        pid  = Data['Subers'][suberKey][MajorOrMinor]['Whip']
        if len(Data['Subers'][suberKey][MajorOrMinor]['Proposal']) > 1:
            for subChan, disChan in list(zipChan): 
                if disChan == 'voting': continue
                if Data[subChan]['ProposingPlayer'] is None:
                    print("Pop Suber", subChan, MajorOrMinor, "into", subChan, disChan )
                    Data[subChan] = { 'Yay':[], 'Nay':[], 'Abstain':[], 'ProposingMSGs':[], 'ProposingPlayer':pid,
                        'Suber':f"Proposal {suberKey}'s SUBER: Suber {Data['Subers'][suberKey][MajorOrMinor]['Party']} Whip:",
                        'ProposingText':                          str(Data['Subers'][suberKey][MajorOrMinor]['Proposal']),
                        'Proposal#':Data['Proposal#'], 'SuberKey':suberKey
                        }
                    Data['Proposal#'] += 1
                    Data['Subers'][suberKey][MajorOrMinor]['Proposal'] = ""
                    Data['Subers'][suberKey][MajorOrMinor]['Supporters'] = []
                    Data['Subers'][suberKey][MajorOrMinor]['DOB'] = now()

                    print('..PopProposal To Suber: ',suberKey, MajorOrMinor)
                    await payload['refs']['channels'][disChan].set_permissions(payload['refs']['roles']['Player'], send_messages=True)
                    break

    await updateProposal(Data, payload)
    await create_queue(Data, payload, )
    await create_array(Data, payload, )

async def yay(Data, payload):
    author = payload['Author ID']
    channelMap = {
        'voting': 'Votes',
        'voting-1': 'Suber-Votes-1',
        'voting-2': 'Suber-Votes-2',
        'voting-3': 'Suber-Votes-3',
        'voting-4': 'Suber-Votes-4',
    }
    voteKey = channelMap[payload['Channel']]
    if author not in Data[voteKey]['Yay']:           Data[voteKey]['Yay'].append( author )
    if author in Data[voteKey]['Nay']:               Data[voteKey]['Nay'].remove( author )
    if author in Data[voteKey]['Abstain']:           Data[voteKey]['Abstain'].remove( author )
    #await payload['message'].remove_reaction(nayEmoji , payload['user'])

async def nay(Data, payload):
    author = payload['Author ID']
    channelMap = {
        'voting': 'Votes',
        'voting-1': 'Suber-Votes-1',
        'voting-2': 'Suber-Votes-2',
        'voting-3': 'Suber-Votes-3',
        'voting-4': 'Suber-Votes-4',
    }
    voteKey = channelMap[payload['Channel']]
    if author not in Data[voteKey]['Nay']:           Data[voteKey]['Nay'].append( author )
    if author in Data[voteKey]['Yay']:               Data[voteKey]['Yay'].remove( author )
    if author in Data[voteKey]['Abstain']:           Data[voteKey]['Abstain'].remove( author )
    #await payload['message'].remove_reaction(yayEmoji , payload['user'])

async def abstain(Data, payload):
    author = payload['Author ID']
    channelMap = {
        'voting': 'Votes',
        'voting-1': 'Suber-Votes-1',
        'voting-2': 'Suber-Votes-2',
        'voting-3': 'Suber-Votes-3',
        'voting-4': 'Suber-Votes-4',
    }
    voteKey = channelMap[payload['Channel']]
    if author not in Data[voteKey]['Abstain']:       Data[voteKey]['Abstain'].append( author )
    if author in Data[voteKey]['Yay']:               Data[voteKey]['Yay'].remove( author )
    if author in Data[voteKey]['Nay']:               Data[voteKey]['Nay'].remove( author )
    #await payload['message'].remove_reaction(nayEmoji , payload['user'])

"""
Function Called on Reaction
"""
async def on_reaction(Data, payload):
    isInactive = payload['raw'].author.get_role(payload['refs']['roles']['Inactive'].id) is not None

    if payload['Channel'] == 'voting' and False:
       
        if payload['emoji'] == yayEmoji:
            await yay(Data, payload)
            await payload['message'].add_reaction('✔️')
        if payload['emoji'] == nayEmoji:            
            await nay(Data, payload)
            await payload['message'].add_reaction('✔️')
        elif vote in ['abstain', 'withdraw']:
            await abstain(Data, payload)
            await payload['message'].add_reaction('✔️')

    if payload['Channel'] == 'queue' and payload['mode'] == 'add':

        await payload['message'].remove_reaction(payload['emoji'] , payload['user'])
        if len(payload['Attachments']) == 0: return Data
        author   = int(list(payload['Attachments'].keys())[0].split("-")[0])
        
        if payload['emoji'] == '👍':
            if payload['user'].id not in Data['PlayerData'][author]['Proposal']['Supporters']:
                Data['PlayerData'][author]['Proposal']['Supporters'].append(payload['user'].id)
            await create_queue(Data, payload)

        elif payload['emoji'] == '👎':
            if payload['user'].id in Data['PlayerData'][author]['Proposal']['Supporters']:
                Data['PlayerData'][author]['Proposal']['Supporters'].remove(payload['user'].id)
            await create_queue(Data, payload)

        elif payload['emoji'] == 'ℹ️':
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
        else: return

        # If Inactive, Make Active
        if isInactive and Data['PlayerData'][author]['Inactive'] is None:
            await p.remove_roles(payload['refs']['roles']['Inactive'])
        
        if isInactive and Data['PlayerData'][author]['Inactive'] is "315":
            Data['PlayerData']['Inactive'] = None            
            await p.remove_roles(payload['refs']['roles']['Inactive'])
    
    if payload['Channel'] == 'array' and payload['mode'] == 'add':

        await payload['message'].remove_reaction(payload['emoji'] , payload['user'])

        # If not "Is Official"
        if len(payload['Attachments']) == 0: return Data

        suberKey     = int(list(payload['Attachments'].keys())[0].split("-")[1])
        MajorOrMinor = list(payload['Attachments'].keys())[0].split("-")[2]
        
        if suberKey not in Data['Subers']:
            print("Failed Suber Emoji", Data['Subers'].keys(), suberKey)
            return

        if payload['emoji'] == '🎗️':
            if not Data['Subers'][suberKey][MajorOrMinor]['Is Official']:
                for i in Data['Subers'][suberKey][MajorOrMinor]['Whip']: 
                    if i['Name'] == payload['user'].id: return
                if payload['user'].id not in Data['Subers'][suberKey][MajorOrMinor]['Members']: 
                    await payload['user'].send( content = "You are not a member of this Suber Side")
                    return
                if not Data['Subers'][suberKey][Data['Subers'][suberKey]['Loser']]['Is Official'] and Data['Subers'][suberKey]['Loser'] != MajorOrMinor:
                    await payload['user'].send( content = "You must wait for the Minority Whip To be Elected before nominating Majority Whips")
                    return
                Data['Subers'][suberKey][MajorOrMinor]['Whip'].append({'Name':payload['user'].id, 'Supporters':[], 'DOB':now()})
                await create_array(Data, payload)
        
        if payload['emoji'] in whipEmojiMap:
            if not Data['Subers'][suberKey][MajorOrMinor]['Is Official']:
                endorsedIndex = whipEmojiMap.index(payload['emoji'])
                if payload['user'].id not in Data['Subers'][suberKey][MajorOrMinor]['Members']: 
                    await payload['user'].send( content = "You are not a member of this Suber Side")
                    return
                if payload['user'].id in Data['Subers'][suberKey][MajorOrMinor]['Whip'][endorsedIndex]['Supporters']: 
                    return
                if endorsedIndex < len(Data['Subers'][suberKey][MajorOrMinor]['Whip']):
                    for whipKey in range(len(Data['Subers'][suberKey][MajorOrMinor]['Whip'])):
                        if payload['user'].id in Data['Subers'][suberKey][MajorOrMinor]['Whip'][whipKey]['Supporters']:
                            Data['Subers'][suberKey][MajorOrMinor]['Whip'][whipKey]['Supporters'].remove(payload['user'].id)                    
                    Data['Subers'][suberKey][MajorOrMinor]['Whip'][endorsedIndex]['Supporters'].append(payload['user'].id)
                            
                    await create_array(Data, payload)

        if Data['Subers'][suberKey][MajorOrMinor]['Is Official'] and payload['emoji'] == '👍':
            if payload['user'].id not in Data['Subers'][suberKey][MajorOrMinor]['Supporters']:
                Data['Subers'][suberKey][MajorOrMinor]['Supporters'].append(payload['user'].id)
            await create_array(Data, payload)

        if Data['Subers'][suberKey][MajorOrMinor]['Is Official'] and payload['emoji'] == '👎':
            if payload['user'].id in Data['Subers'][suberKey][MajorOrMinor]['Supporters']:
                Data['Subers'][suberKey][MajorOrMinor]['Supporters'].remove(payload['user'].id)
            await create_array(Data, payload)

        if Data['Subers'][suberKey][MajorOrMinor]['Is Official'] and payload['emoji'] == 'ℹ️':
            msg = f"**\nProposal {suberKey}'s SUBER: Suber {Data['Subers'][suberKey][MajorOrMinor]['Party']} Whip Supporters:**\n"
            for p in Data['Subers'][suberKey][MajorOrMinor]['Supporters']: msg += '\n - ' + Data['PlayerData'][p]['Name']
            msg += "\n"
            await payload['user'].send(msg)

            msg = f"**\nProposal {suberKey}'s SUBER: Suber {Data['Subers'][suberKey][MajorOrMinor]['Party']} Whip Proposal:**\n"
            for line in Data['Subers'][suberKey][MajorOrMinor]['Proposal'].split('\n'):
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
    
    if payload['Channel'] == 'DM' and payload['mode'] == 'add' and \
        Data['PlayerData'][payload['user'].id]['Query'] is not None and \
        Data['PlayerData'][payload['user'].id]['Query']["msgid"] == payload['message'].id:
            if Data['PlayerData'][payload['user'].id]['Query']["Type"] == 'ArrayProposal':
                suberKey     = Data['PlayerData'][payload['user'].id]['Query']["Options"][payload['emoji']][0]
                MajorOrMinor = Data['PlayerData'][payload['user'].id]['Query']["Options"][payload['emoji']][1]
                
                Data['Subers'][suberKey][MajorOrMinor]['Proposal']   = str(Data['PlayerData'][payload['user'].id]['Query']["ProposalText"])
                Data['Subers'][suberKey][MajorOrMinor]['DOB']        = now()
                Data['Subers'][suberKey][MajorOrMinor]['Supporters'] = [payload['user'].id, ]
                
                Data['PlayerData'][payload['user'].id]['Query'] = None 

                await payload['message'].add_reaction('✔️')
                await create_array(Data, payload, )

    return Data


"""
Main Run Function On Messages
"""
async def on_message(Data, payload):
    isInactive = payload['raw'].author.get_role(payload['refs']['roles']['Inactive'].id) is not None

    if payload['Channel'] in ['voting',]:

        # Remove MSG if from a non Player (Bot, Illegal, Etc)
        if payload['Author ID'] not in Data['PlayerData'] or not Data['VotingEnabled']:
            print('Removing', payload['Content'])
            await payload['raw'].delete()
            return
        
        # Handle Incactivity
        if isInactive and Data['PlayerData'][payload['Author ID']]['Inactive'] is None:
            await p.remove_roles(payload['refs']['roles']['Inactive'])
        
        if isInactive and Data['PlayerData'][payload['Author ID']]['Inactive'] is "315":
            await payload['raw'].author.send( content = "You must endorse a proposal to become active again. (Rule 315)")
            return
            
        # Register Vote
        vote = payload['Content'].lower().strip()
        if vote in [ "aye", "yay", "yes", "y", "ye", "pog", "ya", "noice", "cash money", "yeah", "heck yeah", "hell yeah"]:
            await yay(Data, payload)
            await payload['raw'].add_reaction('✔️')
        elif vote in ["nay", "no", "n", "nah", "nein", "sus", "cringe", "soggy"]:
            await nay(Data, payload)
            await payload['raw'].add_reaction('✔️')
        elif vote in ['abstain', 'withdraw']:
            await abstain(Data, payload)
            await payload['raw'].add_reaction('✔️')
        else:
            await payload['raw'].add_reaction('❌')
            await payload['raw'].author.send( content = "Your vote is ambigious, Please use appropriate yay, nay, or withdraw text." )

        await updateProposal(Data, payload)

    if payload['Channel'] in ['voting-1','voting-2', 'voting-3', 'voting-4']:

        # Remove MSG if from a non Player (Bot, Illegal, Etc)
        if payload['Author ID'] not in Data['PlayerData'] or day < (now() - Data['CurrTurnStartTime']):
            print('Removing', payload['Content'])
            await payload['raw'].delete()
            return
        
        # Handle Incactivity
        if isInactive and Data['PlayerData'][payload['Author ID']]['Inactive'] is None:
            await p.remove_roles(payload['refs']['roles']['Inactive'])
        
        if isInactive and Data['PlayerData'][payload['Author ID']]['Inactive'] is "315":
            await payload['raw'].author.send( content = "You must endorse a proposal to become active again. (Rule 315)")
            return
            
        # Register Vote
        vote = payload['Content'].lower().strip()
        if vote in [ "aye", "yay", "yes", "y", "ye", "pog", "ya", "noice", "cash money", "yeah", "heck yeah", "hell yeah"]:
            await yay(Data, payload)
            await payload['raw'].add_reaction('✔️')
        elif vote in ["nay", "no", "n", "nah", "nein", "sus", "cringe", "soggy"]:
            await nay(Data, payload)
            await payload['raw'].add_reaction('✔️')
        elif vote in ['abstain', 'withdraw']:
            await abstain(Data, payload)
            await payload['raw'].add_reaction('✔️')
        else:
            await payload['raw'].add_reaction('❌')
            await payload['raw'].author.send( content = "Your vote is ambigious, Please use appropriate yay, nay, or withdraw text." )

        await updateProposal(Data, payload)

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
        if Data['VotingEnabled'] == True: 
            await payload['refs']['channels']['deck-edits'].send("The deck cannot be updated at this time in the turn.")
            return
        if payload['Author ID'] != Data['Votes']['ProposingPlayer']: 
            await payload['refs']['channels']['deck-edits'].send("You are not the proposer. This message will be ignored.")
            return

        if len(payload['Attachments']) == 1 and '.txt' in list(payload['Attachments'].keys())[0]:
            decoded = await list(payload['Attachments'].values())[0].read()
            decoded = decoded.decode(encoding="utf-8", errors="strict")
            Data['Votes']['ProposingText'] = decoded

        if len(payload['Attachments']) == 0:
            Data['Votes']['ProposingText'] = payload['Content']
        await updateProposal(Data, payload, )

    if payload['Channel'] == 'suber-proposals':
        isWhipFor = []
        pid = payload['Author ID']
        for suberKey in Data['Subers'].keys():
            for MajorOrMinor in ['Assenter', 'Dissenter']:
                if Data['Subers'][suberKey][MajorOrMinor]['Is Official'] and payload['Author ID'] == Data['Subers'][suberKey][MajorOrMinor]['Whip']:
                    isWhipFor.append([suberKey, MajorOrMinor])

        if   len(isWhipFor) == 0:
             await payload['raw'].author.send( content = "You are not a WHIP for any SUBERs")
        
        elif len(isWhipFor) == 1:
            suberKey     = isWhipFor[0][0]
            MajorOrMinor = isWhipFor[0][1]

            if len(payload['Attachments']) == 1 and '.txt' in list(payload['Attachments'].keys())[0]:
                decoded = await list(payload['Attachments'].values())[0].read()
                decoded = decoded.decode(encoding="utf-8", errors="strict")
                Data['Subers'][suberKey][MajorOrMinor]['Proposal'] = str(decoded)

            if len(payload['Attachments']) == 0:
                Data['Subers'][suberKey][MajorOrMinor]['Proposal'] = str(payload['Content'])

            print("Prop:", Data['Subers'][suberKey][MajorOrMinor]['Proposal'])
            Data['Subers'][suberKey][MajorOrMinor]['DOB']        = now()
            Data['Subers'][suberKey][MajorOrMinor]['Supporters'] = [pid, ]
            await create_array(Data, payload)
             
        elif len(isWhipFor) > 1:
            cont = "Please indicate which SUBER you are Proposing to:"
            options = {}
            for i in range(len(isWhipFor)):                
                suberKey     = isWhipFor[i][0]
                MajorOrMinor = isWhipFor[i][1]
                cont += f"\n   {whipEmojiMap[i]} : Proposal {suberKey}'s SUBER"
                options[whipEmojiMap[i]] = isWhipFor[i]

            msg = await payload['raw'].author.send( content = cont)
            if len(payload['Attachments']) == 1 and '.txt' in list(payload['Attachments'].keys())[0]:
                decoded = await list(payload['Attachments'].values())[0].read()
                proposalText = decoded.decode(encoding="utf-8", errors="strict")
            if len(payload['Attachments']) == 0:
                proposalText = payload['Content']
            
            for e in whipEmojiMap[:len(isWhipFor)]: 
                await msg.add_reaction(e)

            Data['PlayerData'][pid]['Query'] = {
                "Type": 'ArrayProposal',
                "Options": options,
                "ProposalText": proposalText,
                "msgid": msg.id
            }
            await create_array(Data, payload, )
        
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
    

    if hold_for_update_prop and last_update_prop_time +5 < time.time():
        await actuallyUpdateVotingProposal(Data, payload)

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
    messages = [m async for m in payload['refs']['channels']['queue'].history(limit=100)]
    Data['Queue'] = sortedQ[::-1]


    # If Queue Structure not right size, regenerate to keep uniform spacing.
    if len(messages) != len(sortedQ): 
        await payload['refs']['channels']['queue'].purge()
        messages = []
        for pid in sortedQ:  
            msg = await payload['refs']['channels']['queue'].send("Generating Proposal View")
            messages.append(msg)
            for r in ['👍', '👎', 'ℹ️']: await msg.add_reaction(r)
    messages = messages[::-1]

    endorsingPlayers = set()

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
            endorsingPlayers.update(Data['PlayerData'][pid]['Proposal']['Supporters'])
        

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
    
    for player in Data['PlayerData'].keys():

        isInactive = payload['refs']['players'][player].get_role(payload['refs']['roles']['Inactive'].id) is not None

        if player not in endorsingPlayers and not isInactive:
            print(player)
            await payload['refs']['players'][player].add_roles(payload['refs']['roles']['Inactive'])
            Data['PlayerData'][player]['Inactive'] = "315"
            await payload['refs']['players'][player].send("You are now Inactive because you are not endorsing any proposals. Endorse a proposal or create one to become active again. (Rule 315)")

    
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
        Data['Turn'] = -1

    if 'Subers' not in Data:
        Data['Subers'] = dict()
    
    if 'Array' not in Data:
        Data['Array'] = dict()

    if 'Queue' not in Data:
        Data['Queue'] = {}

    if 'VotingEnabled' not in Data:
        Data['VotingEnabled'] = False

    if 'ProposingPlayer' in Data:
        Data['Votes']['ProposingPlayer'] = Data['ProposingPlayer']
        del Data['ProposingPlayer']

    if 'ProposingText' in Data:
        Data['Votes']['ProposingText'] = Data['ProposingText']
        del Data['ProposingText']

    if 'ProposingMSGs' in Data:
        Data['Votes']['ProposingMSGs'] = Data['ProposingMSGs']
        del Data['ProposingMSGs']

    if 'Proposal#' not in Data['Votes']:
        Data['Votes']['Proposal#'] = Data['Proposal#']
    
    if 'DeckMSGs' not in Data:
        Data['DeckMSGs'] = []

    if 'CurrTurnStartTime' not in Data:
         Data['CurrTurnStartTime'] = 0

    if 'NextTurnStartTime' not in Data:
         Data['NextTurnStartTime'] = 0

    if 'Votes' not in Data:
         Data['Votes']         = {'Yay':[], 'Nay':[], 'Abstain':[], 'Proposal': {}, 'ProposingMSGs':{},
                                  'ProposingPlayer':None, 'ProposingText':"", 'Proposal#':0 }

    if 'Suber-Votes-1' not in Data:
         Data['Suber-Votes-1'] = {'Yay':[], 'Nay':[], 'Abstain':[], 'Proposal': {}, 'ProposingMSGs':{},
                                  'ProposingPlayer':None, 'ProposingText':"", 'Proposal#':0 , 'Suber':""}

    if 'Suber-Votes-2' not in Data:
         Data['Suber-Votes-2'] = {'Yay':[], 'Nay':[], 'Abstain':[], 'Proposal': {}, 'ProposingMSGs':{},
                                  'ProposingPlayer':None, 'ProposingText':"", 'Proposal#':0 , 'Suber':""}

    if 'Suber-Votes-3' not in Data:
         Data['Suber-Votes-3'] = {'Yay':[], 'Nay':[], 'Abstain':[], 'Proposal': {}, 'ProposingMSGs':{},
                                  'ProposingPlayer':None, 'ProposingText':"" , 'Proposal#':0 , 'Suber':""}

    if 'Suber-Votes-4' not in Data:
         Data['Suber-Votes-4'] = {'Yay':[], 'Nay':[], 'Abstain':[], 'Proposal': {}, 'ProposingMSGs':{},
                                  'ProposingPlayer':None, 'ProposingText':"" , 'Proposal#':0 , 'Suber':""}

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

        if 'Color' not in Data['PlayerData'][pid]:
             Data['PlayerData'][pid]['Color'] = {'Hue':"None", "time": 0}

        if 'Query' not in Data['PlayerData'][pid]:
             Data['PlayerData'][pid]['Query'] = None

        if 'Inactive' not in Data['PlayerData'][pid]:
             Data['PlayerData'][pid]['Inactive'] = None

    for pid in dict(Data['PlayerData']):
        if 'Name' not in Data['PlayerData'][pid]:
            del Data['PlayerData'][pid]
            continue
        for propId in dict(Data['PlayerData']):
            Data['PlayerData'][propId]['Proposal']['Supporters'] = [pid if Data['PlayerData'][pid]['Name'] == x else x for x in Data['PlayerData'][propId]['Proposal']['Supporters']]


    print('Players In Game:',len(Data['PlayerData']))

   
    await create_queue(Data, payload)
    await create_array(Data, payload)
    return await create_queue(Data, payload)
