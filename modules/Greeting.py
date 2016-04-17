import discord
import re
import asyncio 
import time

class Module(object):
	def __init__(self, wrapper):
		self.memberUpdateHooks = [
			Greetings('Welcome back {0.name} you lil bitch!')
		]		
		
class Greetings(object):
	def __init__(self, message):
		self.time = time()
		self.message = message
    
	def __call__(self, changed, before, after): 
		if not changed == 'status':
			return None			
		if before.status==discord.Status.offline and after.status==discord.Status.online:
			if time.time()-self.time>10:
				self.time=time.time()  
				yield from client.send_message(after.server, self.message.format(after))
