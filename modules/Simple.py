import discord
import re
import asyncio

class Module(object):
	def __init__(self):
		pass

	def register(self,client):
		client.messageHooks[re.compile('^!hello$')] = StringReply('Hello {0.author.mention}')
		client.messageHooks[re.compile('^!help$')] = StringReply('Try !hello, !top or !source') 
		client.messageHooks[re.compile('^!source$')] = StringReply('My source is located at https://github.com/Tommassino/LilBitchBot')		
		
class StringReply(object):
	def __init__(self, message):
		self.message=message
    
	def __call__(self, orig_message, match, client): 
		msg = self.message.format(orig_message)
		yield from client.send_message(orig_message.channel,msg)
