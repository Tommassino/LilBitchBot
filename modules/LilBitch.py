import discord
import re
import asyncio
import operator
import time

class Module(object):
	def __init__(self, wrapper):
		self.bitchCounter = wrapper.money
		self.messageHooks = {
			re.compile('.*lil.*bitch.*', flags=re.IGNORECASE): UserIncrement(self.bitchCounter),
			re.compile('.*who.*lil.*bitch.*', flags=re.IGNORECASE): ReplyTop(self.bitchCounter),
			re.compile('^!top$'): ListTop(self.bitchCounter,3),
			re.compile('^am i a lil bitch.*$', flags=re.IGNORECASE): ListBitch(self.bitchCounter)
		}

class UserIncrement(object):
	def __init__(self, user_dict):
		self.user_dict=user_dict
		self.timeout_dict={}
		self.timeout=10

	def __call__(self, orig_message, match,client):
		tm=time.time()
		if orig_message.author.id in self.timeout_dict and tm-self.timeout_dict[orig_message.author.id] < 10:
			return None
		self.timeout_dict[orig_message.author.id]=tm
		self.user_dict.add_money(orig_message.author, 1)
		return None

class ListBitch(object):
	def __init__(self, dict):
		self.dict=dict

	def __call__(self, msg, mc, cl):
		count=self.dict.get_money(msg.author)
		yield from cl.send_message(msg.channel,"You have {0} lil bitches!".format(count))

class ListTop(object):
	def __init__(self, dict, top):
		self.dict=dict
		self.top=top

	def __call__(self, msg, mc,client):
		sorted_dict = self.dict.get_top(self.top)
		message = 'The top lil bitches:'
		for i in range(0, len(sorted_dict)):
			item = sorted_dict[i]
			message=message+"\n{0}: {1}".format(item[0],item[1])
		yield from client.send_message(msg.channel,message)

class ReplyTop(object):
	def __init__(self, dict):
		self.dict=dict

	def __call__(self,msg,mc,client):
		sorted_dict = self.dict.get_top(1)
		if len(sorted_dict)>0:
			top = sorted_dict[0]
			yield from client.send_message(msg.channel,"{0} is a lil bitch!".format(top[0]))
