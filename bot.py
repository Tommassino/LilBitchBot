import discord
import asyncio
import json
import time
from os.path import isfile
import glob
import importlib
from importlib.machinery import SourceFileLoader


class ClientConfig(object):
	def __init__(self, client, configPath):
		self.client=client
		self.messageHooks={} 
		self.config = {}
	
		with open(configPath,'r') as fp:
			self.config=json.load(fp)
		
		print('Loading modules...')
		modules = glob.glob("modules/*.py")
		for f in (m for m in modules if isfile(m)):
			dir,mod = f.rsplit('/',1)
			mod,py = mod.rsplit('.',1)
			print('\t{0}'.format(mod))
			module = SourceFileLoader(mod,f).load_module()
			init = module.Module()
			init.register(self)

client = discord.Client()		

wrapper = ClientConfig(client,'config.json')    

@client.event
@asyncio.coroutine
def on_message(message):
	# we do not want the bot to reply to itself
	if message.author == wrapper.client.user:
		return

	for regexp in wrapper.messageHooks:
		print(regexp)
		match = regexp.match(message.content)
		if match:
			yld = wrapper.messageHooks[regexp](message,match,wrapper.client)

			if yld:
				return yld
lasttime=0

@client.event
@asyncio.coroutine
def on_member_update(before, after):
	global lasttime
	for attr in dir(after):
		if not callable(getattr(after,attr)) and not getattr(after,attr)==getattr(before,attr):
			print(attr)
			print(getattr(before,attr))
			print(getattr(after,attr))
	if before.status==discord.Status.offline and after.status==discord.Status.online:
		if time.time()-lasttime>10:
			lasttime=time.time()
			yield from client.send_message(after.server,'Welcome back {0.name} you lil bitch!'.format(before)) 

@client.event
@asyncio.coroutine
def on_ready():
	print('Logged in as')
	print(wrapper.client.user.name)
	print(wrapper.client.user.id)
	print('------')
#	with open('burger_small.jpg','rb') as f:
#		yield from wrapper.client.edit_profile(avatar=f.read())


client.run(wrapper.config['token'])
