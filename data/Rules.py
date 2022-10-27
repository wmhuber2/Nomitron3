#
# Blank Module For Discord Bot
################################
import pickle, sys, urllib, discord, io

"""
Main Run Function On Messages
"""

async def r(Data, payload, *text):
    await rule(Data, payload, *text)

async def rule(Data, payload, *text):
    argv = text[0]
    message = payload['raw']
    rulequery = int(argv[1])
    if(rulequery not in Data['RuleList'].keys()):
        await message.channel.send("I couldn't find that rule.")
    else:
        print("Found Rule", rulequery)
        answer = Data['RuleList'][rulequery]
        answer = answer.replace('\\xe2\\x95\\x9e', ' ')
        answer = answer.replace('\\xe2\\x95\\x90', ' ')
        answer = answer.replace('\\xe2\\x95\\xa1', ' ')
        answer = answer.replace('\\xe2\\x94\\x80', ' ')
        msg = ""

        for line in answer.split('\n'):
            line += '\n'
            if len(msg + line) > 1950:
                await message.channel.send(msg)
                while len(line) > 1900:
                    msgend = line[1900:].index(' ')
                    await  message.channel.send(line[:1900+msgend])
                    line = line[1900+msgend:]
                msg = line
            else: msg += line
        if len(msg) > 0: await  message.channel.send(msg)


async def find(Data, payload, *text):
    argv = text[0]
    query = ' '.join(argv[1:]).lower()
    message = payload['raw']
    if payload['Channel'] in ['game']: return

    if query[ 0] == '"': query = query[1:  ]
    if query[-1] == '"': query = query[ :-1]
    print ('Searching for', query)
    if len(query) <= 3: await message.channel.send("Must Search Words Longer Then 3 Letters")
    else:
        found = False
        rulecount = 5
        roundmsg = ""
        for rule in Data['RuleList'].keys():
            low = Data['RuleList'][rule].lower()

            if query in low and rulecount <= 0:
                roundmsg += str(rule) + ', '
            if query in low and rulecount >= 0:
                rulecount-=1
                isIn = 1
                count = 2
                initIndex = 0
                msg = '`'+str(rule)+':`\n'
                while isIn and count > 0:
                    found = True
                    try:
                        index = low[initIndex:].index(query)
                        index += initIndex

                        initIndex = index + len(query)

                        boundLower = index - 40
                        if boundLower < 0:boundLower = 0

                        boundUpper = index + 120
                        if boundUpper >= len(low): boundUpper = len(low)-1

                        msg +=('\t...'\
                              +Data['RuleList'][rule][boundLower:index]\
                              +'**'+ Data['RuleList'][rule][index:index+len(query)]\
                              +'**'+ Data['RuleList'][rule][index+len(query):boundUpper]\
                              +'...').replace('\n','  ')+'\n\n'
                    except ValueError:
                        isIn = 0
                    count -= 1
                if count <= 0:
                    msg += '...and more...'
                await message.channel.send(msg)
        if len(roundmsg) != 0:
            await message.channel.send('and in rules: '+roundmsg)
        if not found:
            await message.channel.send("Couldn't Find A Match For "+query)

async def f(Data, payload, *text):
	await find(Data, payload, *text)

async def search(Data, payload, *text):
	await find(Data, payload, *text)

"""
Setup Log Parameters and Channel List And Whatever You Need to Check on a Bot Reset.
Handles Change In Server Structure and the like. Probably Can Leave Alone.
"""
async def setup(Data, payload):
    # Do Stuff Here
    Data['RuleList'] = {}
    with urllib.request.urlopen('https://gitlab.com/nomicgame/nomic-vi/-/raw/master/rules.md') as response:
        rules = response.read().decode("utf-8")
        ruletxt = rules.split("## ")[1:]
        print(f'Found {len(ruletxt)} Rules')
        for rule in ruletxt:
            rule = rule.replace('\n',' \n')
            if 1:#try:
                #rule = rule.strip().split('\n\n',1)
                rulenum = rule.split(' ')[0]
                rulenum = int(rulenum)
                Data['RuleList'][rulenum] = rule
            try: pass
            except:
                print('ERROR')
                print(rule)
    return Data
