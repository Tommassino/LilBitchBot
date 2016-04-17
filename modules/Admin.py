import discord
import re
import asyncio

class Module(object):
	def __init__(self):
		pass

	def register(self,client):
		self.admins = client.config['admins']
		client.messageHooks[re.compile('^!kick .*$')] = Kick(self)
		client.messageHooks[re.compile('^!reload .*$')] = ReloadModule(self,client)

class Kick(object):
	def __init__(self, module):
		self.module = module

	def __call__(self, msg, mtc, cli):
		if not msg.author.id in self.module.admins:
			return None
		name=msg.content.split(' ')[1]
		find = None
		for m in msg.author.server.members:
			if m.name==name:
				find=m
				break
		print(find)

		yield from cli.kick(find)
		
class ReloadModule(object):
	def __init__(self, wrapper):
		self.wrapper = wrapper

	def __call__(self, msg, mtc, cli):
		if not msg.author.id in self.module.admins:
			return None
		name=msg.content.split(' ')[1]
		self.wrapper.load_module(name, True)