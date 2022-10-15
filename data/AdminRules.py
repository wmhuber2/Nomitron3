#
# Admin Module For Discord Bot
################################
import sys, os,datetime
from shutil import copyfile


admins = ['Fenris#6136', 'Crorem#6962', 'iann39#8298', 'Alekosen#6969', None]


async def clearAll(Data, payload, *text):
    if payload.get('Author') in admins: 
        messages = [m async for m in payload['raw'].channel.history(limit=200)]
        for msg in messages: await msg.delete()
async def sudo(Data, payload, *text):
    if payload.get('Author') in admins: 
        await payload['refs']['players'][payload['raw'].author.id].add_roles(payload['refs']['roles']['Moderator'])
async def sudont(Data, payload, *text):
    if payload.get('Author') in admins:         
        await payload['refs']['players'][payload['raw'].author.id].remove_roles(payload['refs']['roles']['Moderator'])

    
async def restart(Data, payload, *text):
    message = payload['raw']
    print('Restarting',payload.get('Author'))
    if payload.get('Author') in admins:
        await message.channel.send('Going for Restart')
        print("Going For Restart...")
        sys.exit(0)

async def ping(Data, payload, *text):
    message = payload['raw']
    await message.channel.send('!pong')
"""
Main Run Function
"""
async def on_message(Data, payload):
    message = payload['raw']
    botCharacter = '!'

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

def uploadData(Data, payload):
    k = payload['Attachments'].keys[0]
    newData = yaml.safe_load(payload['Attachments'][k])
    self.Data = dict(newData)
