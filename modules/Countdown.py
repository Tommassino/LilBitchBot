import discord
import re
import asyncio
from datetime import datetime
import pytz


class Module(object):
	def __init__(self, wrapper):
		self.wrapper = wrapper
		self.logger = wrapper.logger
		self.messageHooks = {
			re.compile('^!legion$'): Countdown(self)
		}
		
class Countdown(object):
	def __init__(self, module):
		self.module=module

	def __call__(self, orig_message, match, client):
		launch = datetime(2016,8,29,hour=23,tzinfo=pytz.timezone("CET")).replace(tzinfo=None)
		now = datetime.now().replace(tzinfo=None)
		s = (launch-now).total_seconds()
		ts = "{0:.0f} days {1:.0f} hours {2:.0f} minutes".format(s // (3600*24), s // 3600% 24, s%3600 // 60)
		msg = "**Legion will arive in {0}**\nhttp://i.imgur.com/zfVikwI.png".format(ts)
		yield from client.send_message(orig_message.channel,msg)

