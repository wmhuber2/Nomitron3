from datetime import datetime
import time
import sys, asyncio, os, importlib, glob, datetime, random,socket, multiprocessing, re, yaml
from shutil import copyfile

from threading import Thread
discord = None
import traceback
default_server_id = 707705708346343434
path = "/usr/src/app/"
savefile = 'DiscordBot_Data.yml'
Admins = ['Fenris Wolf#6136', 'Crorem#6962', 'iann39#8298']


'''
Implement Modules By Placing Module Python File In Same Directory
Modules Must Have Different Names And Be Written With Python 3 Compatibility.
Use Blank.py as a Template for new modules.

It is recommended not to edit this file.
'''

class DiscordNomicBot():

    """
    Initialize The Bot Handling Class
    """
    def __init__(self, ):
        try:
            global discord
            discord = importlib.import_module('discord')
            print (discord.__version__)
        except KeyboardInterrupt:# ImportError:
            print ("Discord Library Not Found, install by \"pip install discord\"")
            sys.exit(0)


        self.moduleNames = []
        self.modules = []

        self.refs = {}
        self.Data = {}

        self.loadData()

        for mod in glob.glob("*.py"):
            mod = mod[:-3]
            if not 'Rule' in mod: continue
            print('Importing Module ',mod)
            self.modules.append(importlib.import_module(mod))
            self.moduleNames.append(mod)

        self.loop = asyncio.get_event_loop()
        self.client = discord.Client(loop = self.loop, heartbeat_timeout=120)
        self.token = open(path+'token.secret','r').readlines()[0].strip()
        print("Using Token: ..." + self.token[-6:])

        @self.client.event
        async def on_ready(): await self.on_ready()

        @self.client.event
        async def on_message(message): await self.on_message(message)

        @self.client.event
        async def on_raw_reaction_add(msg): await self.on_raw_reaction(msg, 'add')

        @self.client.event
        async def on_raw_reaction_remove(msg): await self.on_raw_reaction(msg, 'remove')


    def start(self):
        self.client.run(self.token, reconnect=True, )

    """
    Ruturn Channel Type
    """
    def getChannelType(self,obj):
        if type(obj) == discord.channel.DMChannel: return 'DM'
        if type(obj) == discord.channel.TextChannel: return 'Text'
        if type(obj) == discord.channel.GroupChannel: return 'Group'
        return ''


    """
    Convert message data To Easier Message Payload
    """
    def convertToPayload(self, message):
        payload = {}

        if message == None:  return
        payload['raw'] = message
        payload['Author'] = message.author.name + "#" + str(message.author.discriminator)
        payload['Nickname'] = message.author.name
        payload['Channel Type'] = self.getChannelType(message.channel)
        if payload['Channel Type'] == 'Text':
            #payload['Nickname'] = message.author.nick
            payload['Channel'] = message.channel.name
            payload['Category'] = message.guild.get_channel(message.channel.category_id)
        if payload['Channel Type'] == 'DM':
            payload['Channel'] = "DM"
            payload['Category'] = "DM"
        payload['Content'] = message.system_content.strip()
        payload['Attachments'] = {}
        payload['ctx'] = self.client
        payload['Server'] = message.guild
        payload['refs'] = self.refs
        for file in message.attachments:
            payload['Attachments'][file.filename] = file.url
        #print(payload['Content'])
        return payload


    async def passToModule(self, function, payload, *args):
        for mod, name in zip(self.modules, self.moduleNames):
            if hasattr(mod, function):
                try:
                    payload_tmp = None
                    if payload is not None: payload_tmp = dict(payload)
                    if args is None:  tmp = await getattr(mod, function)(self.Data, payload_tmp)
                    else:             tmp = await getattr(mod, function)(self.Data, payload_tmp, *args)

                    if type(tmp) is dict:  self.Data = tmp
                except KeyboardInterrupt as e:
                    await self.servertree[server.id]['mod-lounge'].send(str([e, e.__cause__]))
                    print('Error',e, e.__cause__)

    """
    Display All Server ,Detailssocket.gethostname()
    """
    async def on_ready(self):
        print()
        print('Logged in as ' + self.client.user.name)
        print('Bot Started!')
        print('-'*20)

        try: os.mkdir(path + 'BackupDataFiles/')
        except: pass
        copyfile(path + savefile,
                 path + 'BackupDataFiles/'+ savefile + '-' + str(datetime.datetime.now()))


        self.refs['server'] = self.client.guilds[0]
        self.refs['channels'] = []

        if not 'server' in self.Data:
            print(self.client.guilds[0], self.client.guilds[0].id)
            self.Data['server'] = self.client.guilds[0].id
        if not 'channels' in self.Data:
            self.Data['channels'] = []
        for channel in self.client.guilds[0].text_channels:
            self.Data['channels'].append( channel.id )
            self.refs['channels'].append( channel )
        self.printInfo()

        payload = {'ctx': self.client}
        await self.passToModule('setup', dict(payload))
        self.saveData()
        print('Setup Finished!')

        while 1:
            sys.stdout.flush()
            await asyncio.sleep(8)
            await self.passToModule('update', dict(payload))
            self.saveData()

    """
    Handle Message Event
    """

    async def on_message(self, message):
        if message.author == self.client.user: return
        payload = self.convertToPayload(message)

        found = False
        if payload['Content'].split(' ')[0][0] == '!':
            functionName = payload['Content'][1:].split(' ')[0]
            for i in range(len(self.moduleNames)):
                mod = self.modules[i]
                if hasattr(mod, functionName):
                    if found: print('Duplicate Function of Name '+functionName+' in '+self.moduleNames[i])
                    found = True
                    try:
                        tmp = await self.passToModule(functionName, payload, payload['Content'][1:].split(' ') )
                        if tmp is not None:  self.Data = tmp
                    except Exception as e:
                        print(e, 'Incorrectly Formatted Funtion for '+functionName+' in '+self.moduleNames[i])

        if not found:
            await self.passToModule('on_message', payload)

        sys.stdout.flush()
        self.saveData()

    """
    Handle Reactions
    """
    async def on_raw_reaction(self, payload, mode):
        user = self.client.get_user(payload.user_id)
        if user == self.client.user: return

        channel = self.client.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)

        react_payload = dict(payload)
        react_payload['mode']    = mode
        react_payload['message'] = msg
        react_payload['user']    = user
        react_payload['channel'] = channel
        react_payload['name']    = user.name + '#' + user.discriminator


        server = msg.guild
        await self.passToModule('on_reaction', react_payload)

        if str(payload.emoji) == str('🔄') and react_payload['name'] in Admins: await self.on_message(msg)
        sys.stdout.flush()
        self.saveData()


    """
    Member Greeting And Initialization
    """
    async def on_member_join(self, member):
        await self.passToModule('on_member_join', member)
        self.saveData()

    """
    Save Memory Data From File
    Dont Modify Unless You Really Want To I Guess...
    """
    def saveData(self):
        with open(path + savefile, 'w') as handle:
            yaml.dump(self.Data, handle)

    """
    Load Memory Data From File
    Dont Modify Unless You Really Want To I Guess...
    """
    def loadData(self):
        if not os.path.isfile(path + savefile):
            self.saveData()
        with open(path + savefile, 'r') as handle:
            newData = yaml.safe_load(handle)
            if newData is None:
                with open(path + savefile, 'w') as handle:
                    yaml.dump(self.Data, handle)
            else:
                self.Data = dict(newData)



    """
    Diplay Server Info to Terminal
    """
    def printInfo(self):
        msg = "-" * 24 + "\n" \
              + "Nomitron Bot Booting Up.\n" \
              + "System Time: " + str(datetime.datetime.now()) + '\n' \
              + "Host: " + socket.gethostname() + '\n'

        msg += "\n\nServer: " + str(self.Data['server']) + "\nModules Loaded:"
        for m in self.moduleNames: msg += '\n- ' + m
        print(msg)
        print('-'*24)

print('\n\n')
bot = DiscordNomicBot()
bot.start()
