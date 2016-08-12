import discord
import re
import asyncio 
import time

class Module(object):
	def __init__(self, wrapper):
		self.logger = wrapper.logger
		self.memberUpdateHooks = {
			tuple(['status', discord.Status.offline, discord.Status.online]): Greetings('Welcome back {0.name} you lil bitch!'),
			tuple(['game', None, discord.Game(name='DOTA 2')]): GameAlert('TIME FOR DOTA BITCHES')
		}
		
class Greetings(object):
	def __init__(self, message):
		self.time = time.time()
		self.message = message
    
	def __call__(self, changed, before, after, client): 
		if time.time()-self.time>10:
			self.time=time.time()  
			yield from client.send_message(after.server, self.message.format(after))

class GameAlert(object):
	def __init__(self, message):
		self.message = message

	def __call__(self, changed, before, after, client):
		yield from client.send_message(after.server, self.message.format(after))
