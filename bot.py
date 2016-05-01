import discord
import asyncio
import json
import time
from os.path import isfile
import json
import os.path
import operator
import glob
import importlib
from importlib.machinery import SourceFileLoader

class DictEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__
		
class JsonDictionary(object):
	def __init__(self, name):
		self.dict={}
		self.name=name
		self.names={}
		if os.path.isfile(name):
			self.load_json(name)

	def __setitem__(self,key,value):
		self.dict[key.id]=value
		self.names[key.id]=key.name
		self.save_json(self.name)

	def __getitem__(self,key):
		return self.dict[key.id]

	def __delitem__(self,key):
		del self.dict[key.id]
		del self.names[key.name]
		self.save_json(self.name)

	def __iter__(self):
		return self.dict.items()

	def __len__(self):
		return len(self.dict)

	def __contains__(self,item):
		return self.dict.__contains__(item.id)

	def items(self):
		it = []
		for key,value in self.dict.items():
			it.append((self.names[key],value,))
		return it

	def load_json(self, file):
		with open(file,'r') as fp:
			self.__dict__=json.load(fp)
			return None

	def save_json(self,file):
		with open(file,'w') as fp:
			json.dump(self,fp,cls=DictEncoder)
			
	def get_top(self, amount):		
		sorted_dict = sorted(self.items(), key=operator.itemgetter(1), reverse=True)
		return sorted_dict[:amount]
	
	def get_money(self, user):
		if not user in self:
			return 0
		return self[user]
	
	def add_money(self, user, amount):
		if user not in self:
			self[user]=amount
		else:
			self[user]=self[user]+amount
		

class ClientConfig(object):
	def __init__(self, client, configPath):
		self.client=client
		self.modules = {} 
		self.config = {}
		self.money = JsonDictionary('lilbitch')
	
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
