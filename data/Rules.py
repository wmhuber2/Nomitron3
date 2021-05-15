#
# Blank Module For Discord Bot
################################
import pickle, sys, urllib, discord, io

"""
Main Run Function On Messages
"""

async def rule(Data, payload, *text):
    argv = text[0]
    message = payload['raw']
    rulequery = int(argv[1])
    if(rulequery not in Data['RuleList'].keys()):
        await message.channel.send("I couldn't find that rule.")
    else:
        print("Found Rule", rulequery)
        answer = Data['RuleList'][rulequery]
        response = ""
        for paragraph in answer.split("\n\n"):
            paragraph = paragraph.replace('\\xe2\\x95\\x9e', ' ')
            paragraph = paragraph.replace('\\xe2\\x95\\x90', ' ')
            paragraph = paragraph.replace('\\xe2\\x95\\xa1', ' ')
            paragraph = paragraph.replace('\\xe2\\x94\\x80', ' ')
            if(len(response) + len(paragraph) + 6 > 1850 or paragraph.startswith(">>")):
                #print(response)
                await message.channel.send(response)
                response = ""
            if(paragraph.startswith(">>")):
                fname = paragraph.strip()[2:]
                flink = 'https://raw.githubusercontent.com/dmouscher/nomic/master/Game_4/images/'+fname
                img = None
                with urllib.request.urlopen(flink) as res:
                    print("Loading image: " + fname)
                    img = io.BytesIO(res.read())
                await message.channel.send(file=discord.File(img, fname))
            elif len(paragraph) >1900:
                print('Error: Paragraph too long!!! Length: ', len(paragraph))
                print(paragraph)
            else:
                response = response + "\n\n" + paragraph
        #print(response)
        await message.channel.send(response)

async def find(Data, payload, *text):
    argv = text[0]
    query = ' '.join(argv[1:]).lower()
    message = payload['raw']

    if query[ 0] == '"': query = query[1:  ]
    if query[-1] == '"': query = query[ :-1]
    print (query)
    if len(query) <= 3: await message.channel.send("Must Search Words Longer Then 3 Letters")
    else:
        found = False
        rulecount = 5
        for rule in Data['RuleList'].keys():
            low = Data['RuleList'][rule].lower()

            if query in low and rulecount <= 0:

                await message.channel.send("and in rule "+str(rule))
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
    with urllib.request.urlopen('https://raw.githubusercontent.com/dmouscher/nomic/master/Game_4/rules-s.txt') as response:
        rules = response.read().decode("utf-8")
        ruletxt = rules.split("\n----------------------------------------------------------------------\n")[1:]
        for rule in ruletxt:
            try:
                #rule = rule.strip().split('\n\n',1)
                rulenum = int(rule.split(' ')[1])

                with urllib.request.urlopen('https://raw.githubusercontent.com/dmouscher/nomic/master/Game_4/rules/txt/' + str(rulenum) + '.txt') as ruleresponse:
                    #print("Loading Rule " + str(rulenum))
                    Data['RuleList'][rulenum] = ruleresponse.read().decode("utf-8")#[1].replace('&nbsp;', ' ').replace('\\n', '\n')
            except:
                print('ERROR')
                print(rule)
    return Data
