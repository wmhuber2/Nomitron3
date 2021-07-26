#
# Dice Module For Discord Bot
################################
import pickle, sys, numpy
"""
Main Run Function On Messages
"""
async def roll(Data, payload, *text):
    message = payload['raw']
    argv = text[0]
    diceInfo = argv[1].split('d')
    if len(diceInfo) == 2:
        randNum = numpy.random.randint(1, int(diceInfo[1])+1, int(diceInfo[0]))
        await message.channel.send(str(sum(randNum))+' : '+str(randNum).replace('  ',' ').replace(' ',', '))
