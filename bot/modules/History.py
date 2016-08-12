import discord
import re
import asyncio
import operator
import time
import urllib
import io
import sys
import json
from bot.shared import Command

HISTORY_TABLE = 'message_history'

class Module(object):
	def __init__(self, wrapper):
		self.logger = wrapper.logger
		self.messageHooks = {
			Command(re.compile('^.save ((.*)-)?(.*)$', flags=re.IGNORECASE), Save(wrapper.database), "save", "Usage: !save <name>-<anything>\n\tMake the bot remember anything for later use to later recall it (see recall command). Save your favourite link or quote!"),
			Command(re.compile('^.recall( (.*))?$', flags=re.IGNORECASE), Recall(wrapper.database), "recall", "Usage: !recall <?name>\n\tMake the bot recall a random memory (name optional), or tell it what to remember. See save command.") 
		}
		#create table message_history (id INT PRIMARY KEY AUTO_INCREMENT, server BIGINT, name VARCHAR(255), message TEXT)

class Save(object):
	def __init__(self, database):
		self.database=database

	def __call__(self, msg, match, client):
		
		name=match.group(2)
		text=match.group(3)
		cursor = self.database.cursor()
		cursor.execute("INSERT INTO {0} (server, name, message) VALUES (%s, %s, %s)".format(HISTORY_TABLE), (msg.server.id, name, text))
		self.database.commit()
		return None

class Recall(object):
	def __init__(self, database):
		self.database=database

	def __call__(self, msg, match, client):
		name=match.group(2)
		print(name)
		print(match.group(1))
		cursor = self.database.cursor()
		if name:
			cursor.execute("SELECT name,message FROM {0} WHERE name=%s AND server=%s".format(HISTORY_TABLE), (name, msg.server.id))
		else:
			cursor.execute("SELECT name,message FROM {0} WHERE server=%s ORDER BY RAND() LIMIT 1".format(HISTORY_TABLE), (msg.server.id,))
		text = cursor.fetchone()
		self.database.commit()
		if text:
			if text[0]:
				yield from client.send_message(msg.channel,"{0}-{1}".format(text[0],text[1]))
			else:
				yield from client.send_message(msg.channel,text[1])

