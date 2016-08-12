import discord
import asyncio
import re
import cymysql
from bot.shared import Command

class Module(object):
	def __init__(self, wrapper):
		self.logger = wrapper.logger
		self.database = cymysql.connect(host='127.0.0.1', port=3306, user='crez', passwd='lilbitch', db='fishing')

		self.messageHooks = {
			Command(re.compile('!lastfish', flags=re.IGNORECASE), LastFish(self))
		}

class LastFish(object):
	def __init__(self, module):
		self.module=module

	def __call__(self, msg, match, cl):
		cur = self.module.database.cursor()
		cur.execute("SELECT fish FROM fish_log ORDER BY time DESC LIMIT 1")
		fish = cur.fetchall()[0][0]
		yield from cl.send_message(msg.channel,"Last fish caught is {0}!".format(fish))
