#
# Admin Module For Discord Bot
################################
import sys, os,datetime, discord, random
from pytube import YouTube 

from shutil import copyfile
path = "/usr/src/app/"
savefile = 'DiscordBot_Data.yml'

admins = ['Fenris#6136', 'Crorem#6962', 'iann39#8298', 'Alekosen#6969', None]

async def play(Data, payload, *text):
    # Gets voice channel of message author
        voice_channel = payload['refs']['channels']['general']
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
    if payload.get('Author') in ['Fenris#6136', 'Crorem#6962']:
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
    if payload.get('Author') in admins:
        message = payload['raw']
        print('Restarting',payload.get('Author'))
        await message.channel.send('Going for Restart')
        print("Going For Restart...")
        sys.exit(0)

async def ping(Data, payload, *text):
    message = payload['raw']
    await message.channel.send('!pong')

async def echo(Data, payload, *text):    
    if payload.get('Author') in admins: await message.channel.send(payload['Content'][1:])
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

    if payload['Content'] in [':heart:', '❤️']:
        await message.channel.send('❤️')
    
    if '?' in payload['Content'] and '!' == payload['Content'][0]:
        options = [
         "It is certain.",
         "It is decidedly so.",
         "Without a doubt.",
         "Yes definitely.",
         "You may rely on it.",
         "As I see it, yes.",
         "Most likely.",
         "Outlook good.",
         "Yes.",
         "Signs point to yes.",
         "Reply hazy, try again.",
         "Ask again later.",
         "Better not tell you now.",
         "Cannot predict now.",
         "Concentrate and ask again.",
         "Don't count on it.",
         "My reply is no.",
         "My sources say no.",
         "Outlook not so good.",
         "Very doubtful."]
        
        await message.channel.send(random.choice(options))

def uploadData(Data, payload):
    if payload.get('Author') in admins:
        k = payload['Attachments'].keys[0]
        newData = yaml.safe_load(payload['Attachments'][k])
        return dict(newData)
