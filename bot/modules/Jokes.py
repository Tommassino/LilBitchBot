import discord
import re
import asyncio  
import urllib.request
import html.parser
import json
from bot.shared import Command

class Module(object):
	def __init__(self, wrapper):
		self.logger = wrapper.logger
		self.messageHooks = {
			Command(re.compile('^!chuck$'), RandomJoke("http://api.icndb.com/jokes/random",['value','joke']), "chuck", "Usage: !chuck\n\tAre you bored? Use this command and you will be unbored by our expert entertainer system!")
		#	re.compile('^!joke$'): model.RandomJoke("https://webknox-jokes.p.mashape.com/jokes/random",['joke']),
		}



class RandomJoke(object):
	def __init__(self, url, jsonpath):
		self.parser=html.parser.HTMLParser()
		self.url=url
		self.jsonpath=jsonpath
	
	def __call__(self, msg, mtc, client):
		data=urllib.request.urlopen(self.url).read().decode('utf-8')
		js = json.loads(data)
		current = js
		for last in self.jsonpath:
			current = current[last]
		yield from client.send_message(msg.channel, self.parser.unescape(current))
    
