import discord
import re
import asyncio

class Module(object):
	def __init__(self, wrapper):
		self.logger = wrapper.logger
		self.messageHooks = {
			re.compile('^!hello$'): StringReply('Hello {0.author.mention}'),
			re.compile('^!help$'): StringReply('Try !hello, !top or !source'), 
			re.compile('^!source$'): StringReply('My source is located at https://github.com/Tommassino/LilBitchBot'),
			re.compile('^!guild$'): StringReply('The guild website is http://lessthanthree.guildlaunch.com/')
		}		
		
class StringReply(object):
	def __init__(self, message):
		self.message=message
    
	def __call__(self, orig_message, match, client): 
		msg = self.message.format(orig_message)
		yield from client.send_message(orig_message.channel,msg)
