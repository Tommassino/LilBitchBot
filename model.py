import json
import os.path
import operator
import urllib.request
import html.parser
import asyncio
import time
import discord

voiceChannel=None
class JoinVoice(object):
	def __init__(self,cmd):
		self.cmd=cmd

	def __call__(self,msg,mtc,cli):
		global voiceChannel
		channel_name=msg.content[len(self.cmd):].strip()
		check = lambda c: c.name == channel_name and c.type == discord.ChannelType.voice
		channel = discord.utils.find(check,msg.server.channels)
		if channel is None:
			yield from cli.send_message(msg.channel,"Invalid channel name")
			return
		voiceChannel = yield from cli.join_voice_channel(channel)

class PlaySound(object):
	def __init__(self,cmd):
		self.cmd=cmd

	def __call__(self,msg,mtc,cli):
		global voiceChannel
		file = msg.content[len(self.cmd):].strip()+".wav"
		player = voiceChannel.create_ffmpeg_player(file)
		player.start()


class Kick(object):
	def __init__(self):
		pass

	def __call__(self, msg, mtc, cli):
		if not msg.author.name=='Tommassino':
			return None
		name=msg.content.split(' ')[1]
		find = None
		for m in msg.author.server.members:
			if m.name==name:
				find=m
				break
		print(find)

		yield from cli.kick(find)

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

		

class StringReply(object):
	def __init__(self, message):
		self.message=message
    
	def __call__(self, orig_message, match, client): 
		msg = self.message.format(orig_message)
		yield from client.send_message(orig_message.channel,msg)
    
class UserIncrement(object):
	def __init__(self, user_dict):
		self.user_dict=user_dict
		self.timeout_dict={}
		self.timeout=10

	def __call__(self, orig_message, match,client):
		dict=self.user_dict
		author=orig_message.author.name+':'+orig_message.author.id
		if author not in dict:
			dict[author]=0
		tm=time.time()
		if orig_message.author.id in self.timeout_dict and tm-self.timeout_dict[orig_message.author.id] < 10:
			return None
		self.timeout_dict[orig_message.author.id]=tm
		dict[author]=dict[author]+1
		return None

class ListBitch(object):
	def __init__(self, dict):
		self.dict=dict

	def __call__(self, msg, mc, cl):
		author=msg.author.name+':'+msg.author.id
		count=0
		if author in self.dict:
			count=self.dict[author]
		yield from cl.send_message(msg.channel,"You have {0} lil bitches!".format(count))

class ListTop(object):
	def __init__(self, dict, top):
		self.dict=dict
		self.top=top

	def __call__(self, msg, mc,client):
		sorted_dict = sorted(self.dict.items(), key=operator.itemgetter(1), reverse=True)
		message = 'The top lil bitches:'
		for i in range(0, min(len(self.dict),self.top)):
			item = sorted_dict[i]
			message=message+"\n{0}: {1}".format(item[0].split(':')[0],item[1])
		yield from client.send_message(msg.channel,message)

class ReplyTop(object):
	def __init__(self, dict):
		self.dict=dict

	def __call__(self,msg,mc,client):
		sorted_dict = sorted(self.dict.items(), key=operator.itemgetter(1), reverse=True)
		if len(sorted_dict)>0:
			top = sorted_dict[0]
			yield from client.send_message(msg.channel,"{0} is a lil bitch!".format(top[0].split(':')[0]))
		
class JsonDictionary(object):
	def __init__(self, name):
		self.dict={}
		self.name=name
		if os.path.isfile(name):
			self.load_json(name)

	def __setitem__(self,key,value):
		self.dict[key]=value
		self.save_json(self.name)

	def __getitem__(self,key):
		return self.dict[key]

	def __delitem__(self,key):
		del self.dict[key]
		self.save_json(self.name)

	def __iter__(self):
		return self.dict.items()

	def __len__(self):
		return len(self.dict)

	def __contains__(self,item):
		return self.dict.__contains__(item)

	def items(self):
		return self.dict.items()

	def load_json(self, file):
		with open(file,'r') as fp:
			self.dict=json.load(fp)

	def save_json(self,file):
		with open(file,'w') as fp:
			json.dump(self.dict,fp)
		

