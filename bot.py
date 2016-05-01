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
		self.modules = {} 
		self.config = {}
	
		with open(configPath,'r') as fp:
			self.config=json.load(fp)
		
		print('Loading modules...')
		modules = glob.glob("modules/*.py")
		for f in (m for m in modules if isfile(m)):
			dir,mod = f.rsplit('/',1)
			mod,py = mod.rsplit('.',1)
			print('\t{0}'.format(mod))
			self.load_module(mod)

	def load_module(self, mod):
		file = glob.glob("modules/{0}.py".format(mod))
		if len(file)==0 or not isfile(file[0]):
			return None
		f = file[0]
		module = None
		module = SourceFileLoader(mod,f).load_module()
		init = module.Module(self)
		self.modules[mod]=init

client = discord.Client()		

wrapper = ClientConfig(client,'config.json')    

@client.event
@asyncio.coroutine
def on_message(message):
	# we do not want the bot to reply to itself
	if message.author == wrapper.client.user:
		return

	for moduleName in wrapper.modules:
		module = wrapper.modules[moduleName]
		if not hasattr(module,'messageHooks'):
			continue
		for regexp in module.messageHooks:
			match = regexp.match(message.content)
			if match:
				yld = module.messageHooks[regexp](message,match,wrapper.client)

				if yld:
					return yld

@client.event
@asyncio.coroutine
def on_member_update(before, after):
	global lasttime
	for attr in dir(after):
		if not callable(getattr(after,attr)) and not getattr(after,attr)==getattr(before,attr):
			for moduleName in wrapper.modules:
				module = wrapper.modules[moduleName]
				if not hasattr(module,'memberUpdateHooks'):
					continue
				for hook in module.memberUpdateHooks:
					if hook[0]==attr and getattr(before,attr)==hook[1] and getattr(after,attr)==hook[2]:
						yld = module.memberUpdateHooks[hook](attr, before, after, client)
						if yld:
							return yld 

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
