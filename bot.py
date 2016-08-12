import discord
import asyncio
import sys

from bot.shared import ClientConfig       

client = discord.Client()

@client.event
@asyncio.coroutine
def on_message(message):
	# we do not want the bot to reply to itself
	if message.author == wrapper.client.user:
		return

	modulesConfig = wrapper.config["modules"]
	for moduleName in wrapper.modules:
		module = wrapper.modules[moduleName]
		if not hasattr(module,'messageHooks'):
			continue
		if moduleName in modulesConfig:
			if "enabled" in modulesConfig[moduleName] and not modulesConfig[moduleName]["enabled"]:
				continue
		 
		for command in module.messageHooks:
			match = command.regexp.match(message.content)
			if match:
				yld = command.callback(message,match,wrapper.client)

				if yld:
					return yld

@client.event
@asyncio.coroutine
def on_member_update(before, after):
	global lasttime
	for attr in dir(after):
		if not callable(getattr(after,attr)) and not getattr(after,attr)==getattr(before,attr):
			modulesConfig = wrapper.config["modules"]
			for moduleName in wrapper.modules:
				module = wrapper.modules[moduleName]
				if not hasattr(module,'memberUpdateHooks'):
					continue
				if moduleName in modulesConfig:
					if "enabled" in modulesConfig[moduleName] and not modulesConfig[moduleName]["enabled"]:
						continue
				for hook in module.memberUpdateHooks:
					if hook[0]==attr and getattr(before,attr)==hook[1] and getattr(after,attr)==hook[2]:
						yld = module.memberUpdateHooks[hook](attr, before, after, client)
						if yld:
							return yld
							
@client.event 
@asyncio.coroutine
def on_error(event, *args, **kwargs):      
	excinfo = sys.exc_info()
	wrapper.logger.error("Uncaught exception", exc_info=excinfo)
	wrapper.handler.flush() 

@client.event
@asyncio.coroutine
def on_ready():
	wrapper.logger.info('Logged in as\n{0}\n{1}\n-----'.format(wrapper.client.user.name, wrapper.client.user.id))
#	with open('burger_small.jpg','rb') as f:
#		yield from wrapper.client.edit_profile(avatar=f.read())

wrapper = ClientConfig(client,'config.json')
client.run(wrapper.config['token'])
