import discord
import re
import asyncio
from bot.shared import Command

class Module(object):
	def __init__(self, wrapper):
		self.logger = wrapper.logger
		self.messageHooks = {
			Command(re.compile('^!hello$'), StringReply('Hello {0.author.mention}'), "hello", "Usage: !hello\n\tUse this whenever you are feeling lonely!"), 
			Command(re.compile('^!source$'), StringReply('My source is located at https://github.com/Tommassino/LilBitchBot'), "source", "Usage: !source\n\tA link to the bots github"),
			Command(re.compile('^!guild$'), StringReply('The guild website is http://lessthanthree.guildlaunch.com/'), "guild", "Usage: !guild\n\tOur guilds website!")
		}		
		
class StringReply(object):
	def __init__(self, message):
		self.message=message
    
	def __call__(self, orig_message, match, client): 
		msg = self.message.format(orig_message)
		yield from client.send_message(orig_message.channel,msg)
