import discord
import re
import asyncio

class Module(object):
	def __init__(self):
		pass

	def register(self,client):
		client.messageHooks[re.compile('^!kick .*$')] = Kick()
		client.messageHooks[re.compile('^!hello$')] = StringReply('Hello {0.author.mention}')
		client.messageHooks[re.compile('^!help$')] = StringReply('Try !hello, !top or !source') 
		client.messageHooks[re.compile('^!source$')] = StringReply('My source is located at https://github.com/Tommassino/LilBitchBot')
		
class Kick(object):
	def __init__(self):
		pass

	def __call__(self, msg, mtc, cli):
		if not msg.author.name=='Tommassino': #TODO config
			return None
		name=msg.content.split(' ')[1]
		find = None
		for m in msg.author.server.members:
			if m.name==name:
				find=m
				break
		print(find)

		yield from cli.kick(find)
		
class StringReply(object):
	def __init__(self, message):
		self.message=message
    
	def __call__(self, orig_message, match, client): 
		msg = self.message.format(orig_message)
		yield from client.send_message(orig_message.channel,msg)
