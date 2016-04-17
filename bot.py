import discord
import asyncio
import json
import time
from os.path import dirname, basename, isfile
import glob
import importlib


class ClientConfig(object):
	def __init__(self, configPath):
		self.client=discord.Client()
		self.messageHooks={} 
		config = {}
	
		with open(configPath,'r') as fp:
			config=json.load(fp)
			
		modules = glob.glob("modules/*.py")
		for f in modules if isfile(f):
			print(f)
			module = importlib.import_module(f)
			module.Module().register(self.messageHooks)
		

wrapper = ClientConfig('config.json')    

wrapper.client.run(wrapper.config['token'])

@client.event
@asyncio.coroutine
def on_message(message):
	# we do not want the bot to reply to itself
	if message.author == wrapper.client.user:
		return

	for regexp in handles:
		match = regexp.match(message.content)
		if match:
			yld = handles[regexp](message,match,wrapper.client)

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


