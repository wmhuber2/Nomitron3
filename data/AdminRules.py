#
# Admin Module For Discord Bot
################################
import sys, os,datetime, discord, random
from pytube import YouTube
from shutil import copyfile
path = "/usr/src/app/"
savefile = 'DiscordBot_Data.yml'

admins = ['Fenris#6136', 'Crorem#6962', 'iann39#8298', 'Alekosen#6969', None]
player = None


async def stop(Data, payload, *text):
    global player
    print("stop")
    if player is not None:
        tplayer = player
        tplayer.stop()
        player = None
        await tplayer.disconnect()
        os.remove(path+'music/tmp_music.mp3')
        os.remove(path+'music/tmp_music.mp4')

async def play(Data, payload, *text):
    # grab the user who sent the command
    global player

    user=payload['raw'].author
    voice_channel=user.voice.channel
    channel=None

    yt = YouTube(text[0][1])
    video = yt.streams.filter(only_audio=True).first()    
    out_file = video.download(output_path=path+'music')
    
    base, ext = os.path.splitext(out_file)
    os.rename(out_file, path+'music/tmp_music'+ext)

    # only play music if user is in a voice channel
    if voice_channel != None:
        # grab user's voice channel
        channel=voice_channel.name
        # create StreamPlayer
        player = await voice_channel.connect()
        player.play(discord.FFmpegPCMAudio(path+'music/tmp_music'+ext))
        
    else:
        await print('User is not in a channel.')


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
    message = payload['raw']  
    if payload.get('Author') in admins: await message.channel.send(payload['Content'][6:])
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

async def update(Data, payload):
    global player
    if player is not None and not player.is_playing():
        await player.stop()
        await vc.disconnect()
        os.remove(path+'music/tmp_music.mp4')
        player = None