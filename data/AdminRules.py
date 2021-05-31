#
# Admin Module For Discord Bot
################################
import sys, os,datetime
from shutil import copyfile


async def restart(Data, payload, *text):
    message = payload['raw']
    admins = ['Fenris Wolf#6136', 'Crorem#6962', 'iann39#8298']
    if payload['Author'] in admins:
        await message.channel.send('Going for Restart')
        print("Going For Restart...")
        sys.exit(0)

async def ping(Data, payload, *text):
    message = payload['raw']
    await message.channel.send('!pog')
"""
Main Run Function
"""
async def on_message(Data, payload):
    message = payload['raw']
    admins = ['Fenris Wolf#6136', 'Crorem#6962', 'iann39#8298']
    botCharacter = '!'

    #if '❤' == payload['Content']:
    #   await message.channel.send("I NEED MORE LOVE")

    if payload['Content'] in ['!help', '! help']:
        with open('PlayerREADME.md', 'r') as helpFile:
            help = helpFile.readlines()
            msg = ""
            for line in help:
                if len(msg + line) > 1900:
                    await message.channel.send('```diff\n'+msg+'```')
                    msg = ""
                msg = msg + line
            if msg != "":
                await message.channel.send('```diff\n'+msg+'```')
