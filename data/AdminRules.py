#
# Admin Module For Discord Bot
################################
import sys, os,datetime, discord
from pytube import YouTube 

from shutil import copyfile
path = "/usr/src/app/"
savefile = 'DiscordBot_Data.yml'

admins = ['Fenris#6136', 'Crorem#6962', 'iann39#8298', 'Alekosen#6969', None]

async def play(Data, payload, *text):
    # Gets voice channel of message author
        voice_channel = payload['raw'].author.channel
        channel = None
        if voice_channel != None:
            channel = voice_channel.name
            vc = await voice_channel.connect()
            print(text[1:]) 
            try:      yt = YouTube(text[1:]) 
            except:   print("Connection Error") #to handle exception 
            
            mp4files = yt.filter('mp4') 

            filename = f"{time.time}"
            yt.set_filename(f"{path}ytmp/"+filename)  
            
            d_video = yt.get(mp4files[-1].extension,mp4files[-1].resolution) 
            try:  d_video.download(f"{path}ytmp/") 
            except:  print("Some Error!") 
            print('Task Completed!') 
            
            vc.play(discord.FFmpegPCMAudio(source=f"{path}ytmp/"+filename))
            while vc.is_playing(): sleep(.1)
            await vc.disconnect()
        

async def clearAll(Data, payload, *text):
    for chan in ['actions', 'voting', 'queue', 'deck-edits','proposals']:
        messages = [m async for m in payload['refs']['channels'][chan].history(limit=200)]
        for msg in messages: await msg.delete()
    os.remove(path + savefile)
    sys.exit(0)

async def clear(Data, payload, *text):
    if payload.get('Author') in admins: 
        messages = [m async for m in payload['raw'].channel.history(limit=20)]
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
