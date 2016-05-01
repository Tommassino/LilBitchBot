import discord
import re
import asyncio

class Module(object):
	def __init__(self, wrapper):
		self.admins = wrapper.config['admins']
		self.messageHooks = {
			re.compile('^!kick .*$'): Kick(self),
			re.compile('^!reload .*$'): ReloadModule(self, wrapper),
			re.compile('^!restart$'): Restart(self)
		}

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
	def __init__(self, module, wrapper):
		self.wrapper = wrapper
		self.module = module

	def __call__(self, msg, mtc, cli):
#		print(self.module.admins.index(msg.author.id))
		if not int(msg.author.id) in self.module.admins:
			print(msg.author.id)
			print(self.module.admins[0])
			print(self.module.admins[0]==msg.author.id)
			print(type(msg.author.id))
			print(type(self.module.admins[0]))
			return None
		name=msg.content.split(' ')[1]
		print('Reloading module {0}'.format(name))
		self.wrapper.load_module(name)
		print('Done')

class Restart(object):
	def __init__(self, module):
		self.module=module

	def __call__(self, msg, mtc, cli):
		if int(msg.author.id) in self.module.admins:
			quit()

