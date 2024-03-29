import time, traceback, multiprocessing, re, yaml, socket
import sys, asyncio, os, importlib, glob, datetime, random
from shutil import copyfile
from threading import Thread

botCommandChar = '!'
discord = None
path = "/usr/src/app/"
savefile = 'DiscordBot_Data.yml'
admin = 1057023272220373143 #'Crorem#6962 Sudo'
serverid = 1028425604879634442 # Nomic 6 1043621642938626171 #
Admins = ['Fenris#6136', 'Crorem#6962', 'iann39#8298', 'Alekosen#6969']
BotChannels = ['market', 'actions','off-topic', 'courtroom', 'critic-responses',
               'voting','voting-1','voting-2','voting-3','voting-4',
               'proposals', 'suber-proposals','mod-lounge', 'bot-spam',
               'deck-edits', 'queue', 'DM', 'game', 'combat']

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
        global serverid, admin
        try:
            global discord
            discord = importlib.import_module('discord')
            print ("Discord Version:", discord.__version__)
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
            if mod in ['Blank', 'Nomitron']: continue
            print('Importing Module ',mod)
            self.modules.append(importlib.import_module(mod))
            self.moduleNames.append(mod)

        self.loop = asyncio.new_event_loop()
        intents = discord.Intents.all()
        self.client = discord.Client(loop = self.loop, heartbeat_timeout=120, intents=intents)
        self.token = open(path+'token.secret','r').readlines()[0].strip()
        print("Using Token: ..." + self.token[-6:])

        if self.token[-4:] == '_OL0':
            serverid =  1043621642938626171
            admin = 250132828950364174 #'Crorem#6962'
            
            print('This is a Test Bot')

        @self.client.event
        async def on_ready(): await self.on_ready()

        @self.client.event
        async def on_message(message): await self.on_message(message)

        @self.client.event
        async def on_raw_reaction_add(reaction): await self.on_raw_reaction(reaction, 'add')

        @self.client.event
        async def on_raw_reaction_remove(reaction): await self.on_raw_reaction(reaction, 'remove')


    def start(self):
        self.client.run(self.token, reconnect=True, )

    """
    Ruturn Channel Type
    """
    def getChannelType(self,obj):
        if type(obj) == discord.channelType.private: return 'DM'
        if type(obj) == discord.channelType.group:   return 'DM'
        if type(obj) == discord.channelType.text:    return 'Text'
        if type(obj) == discord.channelType.GroupChannel: return 'Group'
        return ''


    """
    Convert message data To Easier Message Payload
    """
    def convertToPayload(self, message):
        payload = {}

        if message == None:  return
        payload['Server'] = message.guild
        payload['raw'] = message

        payload['Author'] = message.author.name + "#" + str(message.author.discriminator)
        payload['Author ID'] = message.author.id
        payload['Nickname'] = message.author.name

        payload['Channel Type'] = message.channel.type
        
        if payload['Channel Type'] in [discord.ChannelType.private, discord.ChannelType.group]:
            payload['Channel'] = "DM"
            payload['Category'] = "DM"
        else:
            payload['Nickname'] = message.author.nick
            payload['Channel'] = message.channel.name
            #payload['Category'] = message.guild.get_channel(message.channel.category_id)

        payload['Content'] = message.system_content.strip()
        payload['Attachments'] = {}
        payload['ctx']  = self.client
        payload['refs'] = self.refs
        payload['discord'] = discord

        for file in message.attachments:  payload['Attachments'][file.filename] = file
        #if message.author != self.client.user: print(f"Event in {payload['Channel']}:",message.system_content)
        return payload


    async def passToModule(self, function, payload, *args):
        for mod, name in zip(self.modules, self.moduleNames):
            if hasattr(mod, function):
                try:
                    payload_tmp = None
                    if payload is not None: payload_tmp = dict(payload)
                    payload_tmp['refs'] = self.refs
                    if args is None:  tmp = await getattr(mod, function)(self.Data, payload_tmp)
                    else:             tmp = await getattr(mod, function)(self.Data, payload_tmp, *args)

                    if type(tmp) is dict:  self.Data = tmp
                except KeyboardInterrupt as e:
                    await self.servertree[server.id]['mod-lounge'].send(str([e, e.__cause__]))
                    print('Error',e, e.__cause__)

    """
    Display All Server ,Details socket.gethostname()
    """
    async def on_ready(self):
        print()
        print('*Logged in as ' + self.client.user.name)
        print('Bot Started!')
        print('-'*20)

        try: os.mkdir(path + 'BackupDataFiles/')
        except: pass
        copyfile(path + savefile,
                 path + 'BackupDataFiles/'+ savefile + '-' + str(datetime.datetime.now()))


        self.Data['server'] = serverid
        self.Data['admin'] = admin

        for s in self.client.guilds:
            print( 'Found Server:',s.name, s.id, serverid)
            if s.id == self.Data['server']:
                self.Data['server'] = serverid
                self.refs['server'] = s
                print('Joining Server')
                break


        self.Data['channels'] = {}
        self.refs['channels'] = {}
        self.refs['players']  = {}
        self.refs['roles']    = {}

        for role in await self.refs['server'].fetch_roles():
            self.refs['roles'][role.name]= role
        for member in self.refs['server'].members:
            self.refs['players'][member.id]= member
        for channel in await self.refs['server'].fetch_channels():
            self.Data['channels'][channel.name]= channel.id
            self.refs['channels'][channel.name]= channel
        
        
        self.printInfo()

        payload = {'ctx': self.client, 'Server': self.refs['server'], 'refs':self.refs}
        await self.passToModule('setup', dict(payload))
        self.saveData()
        print('Setup Finished!')

        while 1:
            await asyncio.sleep(5)
            payload = {'ctx': self.client, 'Server': self.refs['server'], 'refs':self.refs}
            await self.passToModule('update', dict(payload))
            self.saveData()

    """
    Handle Message Event
    """

    async def on_message(self, message):
        if message.author == self.client.user: return
        if message.author.get_role(self.refs['roles']['Player'].id) is None: return

        payload = self.convertToPayload(message)
        if payload['Channel'] not in BotChannels: return

        found = False
        if len(payload['Content']) > 0 and payload['Content'][0][0] == botCommandChar:
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
                        #raise e
                        print(e, 'Incorrectly Formatted Funtion for '+functionName+' in '+self.moduleNames[i])

        if not found: await self.passToModule('on_message', payload)
        self.saveData()

        copyfile(path + savefile,
                 path + 'BackupDataFiles/'+ savefile + '-' + str(datetime.datetime.now()))

    """
    Handle Reactions
    """
    async def on_raw_reaction(self, payload, mode):
        if self.client.get_user(payload.user_id) == self.client.user: return
        if self.refs['players'][payload.user_id].get_role(self.refs['roles']['Player'].id) is None: return

        user = self.refs['players'][payload.user_id]
        msg = None
        channel = self.client.get_channel(payload.channel_id)
        if channel is None:
            msg = await user.fetch_message(payload.message_id)
        else:
            msg = await channel.fetch_message(payload.message_id)


        react_payload = self.convertToPayload(msg)
        react_payload['raw']     = payload
        react_payload['mode']    = mode
        react_payload['message'] = msg
        react_payload['user']    = user
        react_payload['emoji']   = str(payload.emoji.name)
        react_payload['name']    = user.name + '#' + user.discriminator

        await self.passToModule('on_reaction', react_payload)

        if mode == 'add' and str(payload.emoji) == str('🔄') and react_payload['name'] in Admins: 
            await self.on_message(msg)
            await msg.remove_reaction(str('🔄'), user)

        self.saveData()

        copyfile(path + savefile,
                 path + 'BackupDataFiles/'+ savefile + '-' + str(datetime.datetime.now()))


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
            #input("File Doesnt Exist. Create One?")
            self.saveData()
        with open(path + savefile, 'r') as handle:
            newData = yaml.safe_load(handle)
            if newData is None:
                input("File Is None. Create One?")
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

        msg += "\n\nServer: " + str(self.refs['server'].name) + "\nModules Loaded:"
        for m in self.moduleNames: msg += '\n- ' + m
        print(msg)
        print('-'*24)

print('\n\n')
bot = DiscordNomicBot()
bot.start()
