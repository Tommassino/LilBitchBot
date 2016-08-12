import discord
import re
import asyncio

class Module(object):
	def __init__(self, wrapper):
		self.admins = wrapper.config['admins']
		self.logger = wrapper.logger
		self.messageHooks = {
			re.compile('^!kick .*$'): Kick(self),
			re.compile('^!reload .*$'): ReloadModule(self, wrapper),
			re.compile('^!restart$'): Restart(self),
			re.compile('^!nick .* .*$'): Nickname(self, wrapper)
		}

class Nickname(object):
	def __init__(self, module, wrapper):
		self.module=module
		self.wrapper=wrapper

	def __call__(self, msg, mtc, cli):
		if not int(msg.author.id) in self.module.admins:
			return None
		name=msg.content.split(' ')[1]
		nick=msg.content.split(' ')[2]

		find = None
		for m in msg.author.server.members:
			if m.name==name:
				find=m
				break
		print('Changing nickname of {0.name} to {1}'.format(find,nick))

		yield from cli.change_nickname(find,nick)

class Kick(object):
	def __init__(self, module):
		self.module = module

	def __call__(self, msg, mtc, cli):
		if not int(msg.author.id) in self.module.admins:
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
		self.wrapper.logger.debug(self.module.admins.index(msg.author.id))
		if not int(msg.author.id) in self.module.admins:
			self.wrapper.logger.debug("Unauthorised access to !reload {0} - {1}".format(msg.author,self.module.admins))
			return None
		name=msg.content.split(' ')[1]
		self.wrapper.logger.info('Reloading module {0}'.format(name))
		self.wrapper.load_module(name)

class Restart(object):
	def __init__(self, module):
		self.module=module

	def __call__(self, msg, mtc, cli):
		if int(msg.author.id) in self.module.admins:
			quit()

