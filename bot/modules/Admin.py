import discord
import re
import asyncio
from bot.shared import Command

class Module(object):
	def __init__(self, wrapper):
		self.admins = wrapper.config['admins']
		self.logger = wrapper.logger
		self.messageHooks = {
			Command(re.compile('^!kick .*$'), Kick(self), "kick", "Usage: !kick <username>\n\tKick somebody from the discord, admin-only"),
			Command(re.compile('^!reload .*$'), ReloadModule(self, wrapper), "reload", "Usage: !reload <module>\n\tReloads a bot module, admin-only"),
			Command(re.compile('^!restart$'), Restart(self), "reload", "Usage: !restart\n\tRestarts the bot, admin-only"),
			Command(re.compile('^!nick .* .*$'), Nickname(self, wrapper), "nick", "Usage: !nick <name> <nickname>\n\tChanges the nickname of somebody, admin-only"),
			Command(re.compile('^!help$'), Help(self, wrapper), "help", "Usage: !help <?command>\n\tDisplays helpful information about the bot or a command"),
			Command(re.compile('^!help (.*)$'), HelpCommand(self, wrapper))
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
		if not int(msg.author.id) in self.module.admins:
			self.wrapper.logger.debug("Unauthorised access to !reload {0} - {1}".format(msg.author,self.module.admins))
			return None
		#self.wrapper.logger.debug(self.module.admins.index(msg.author.id))
		name=msg.content.split(' ')[1]
		self.wrapper.logger.info('Reloading module {0}'.format(name))
		self.wrapper.load_module(name)

class Restart(object):
	def __init__(self, module):
		self.module=module

	def __call__(self, msg, mtc, cli):
		if int(msg.author.id) in self.module.admins:
			quit()

class Help(object):
	def __init__(self, module, wrapper):
		self.module=module
		self.wrapper=wrapper

	def __call__(self, msg, mtc, cli):
		if int(msg.author.id) not in self.module.admins:
			return
		
		message = "To get help on a specific command use !help <command name>\nThe list of available commands: {0}"
		commands = []
		
		for module in self.wrapper.modules:
			if hasattr(self.wrapper.modules[module], 'messageHooks'):
				for command in self.wrapper.modules[module].messageHooks:
					if command.name:
						commands.append(command.name)
		yield from cli.send_message(msg.channel,message.format(', '.join(commands)))
			 
class HelpCommand(object):
	def __init__(self, module, wrapper):
		self.module=module
		self.wrapper=wrapper

	def __call__(self, msg, match, cli):
		if int(msg.author.id) not in self.module.admins:
			return
			
		commandName = match.group(1)
		command = None
		
		for module in self.wrapper.modules:
			if hasattr(self.wrapper.modules[module], 'messageHooks'):
				for cmd in self.wrapper.modules[module].messageHooks:
					if cmd.name and cmd.name==commandName:
						command = cmd
		yield from cli.send_message(msg.channel,command.description)