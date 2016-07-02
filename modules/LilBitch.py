import discord
import re
import asyncio
import operator
import time
from PIL import Image, ImageOps, ImageDraw
import urllib
import io
import sys
import json

class Module(object):
	def __init__(self, wrapper):
		self.bitchCounter = wrapper.money
		self.messageHooks = {
			re.compile('.*lil.*bitch.*', flags=re.IGNORECASE): UserIncrement(self.bitchCounter),
			re.compile('.*who.*lil.*bitch.*', flags=re.IGNORECASE): ReplyTop(self.bitchCounter),
			re.compile('^!top$'): ListTop(self.bitchCounter,3),
			re.compile('^am i a lil bitch.*$', flags=re.IGNORECASE): ListBitch(self.bitchCounter),
			re.compile('^!drawTop$', flags=re.IGNORECASE): DrawTop(wrapper.money,3,wrapper)
		}
		self.lastSpendTime = {}

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
		self.devalue()
		sorted_dict = self.dict.get_top(self.top)
		message = 'The top lil bitches:'
		for i in range(0, len(sorted_dict)):
			item = sorted_dict[i]
			message=message+"\n{0}: {1:.2f}".format(item[0],item[1])
		yield from client.send_message(msg.channel,message)

	def devalue(self):
		now = time.time()
		count = len(self.dict.dict.items())
		for id,value in self.dict.dict.items():
			spent = self.dict.get_lastSpent(id)
#			print("{0}: {1} - {2}".format(id,value,now-spent))
			if now-spent>86400: #devalue
				value_devalue = value*0.1
				self.dict.dict[id]=value-value_devalue
				for add_id, add_value in self.dict.dict.items():
					self.dict.dict[add_id]=value_devalue/count+add_value
				self.dict.lastSpend[id]=time.time()
		self.dict.save()
#			self.dict.lastSpend[id]=time.time()

class ReplyTop(object):
	def __init__(self, dict):
		self.dict=dict

	def __call__(self,msg,mc,client):
		sorted_dict = self.dict.get_top(1)
		if len(sorted_dict)>0:
			top = sorted_dict[0]
			yield from client.send_message(msg.channel,"{0} is a lil bitch!".format(top[0]))

class DrawTop(object):
	def __init__(self, dict, top, wrapper):
		self.dict=dict
		self.top=top
		self.wrapper=wrapper

	def find_member(self, members, user_id):
		for member in members:
			if member.id==user_id:
				return member
		return None
	
	def __call__(self,msg,mc,client):
		top_users = self.dict.get_top_id(self.top)
		pic_path = self.wrapper.config['top_path']
		avatar_locations = self.wrapper.config['top_locations']
		column_locations = self.wrapper.config['column_locations']
		orig = Image.open(pic_path, 'r')
		id=0
		hds = {
			"User-Agent": 'Python/{0[0]}.{0[1]}'.format(sys.version_info)
		}
		
		mask = Image.open('mask.png').convert('L')

		for user in top_users:
			id=id+1
			member = self.find_member(msg.server.members, user[0])

			if member.avatar_url:
				req = urllib.request.Request(member.avatar_url, headers=hds)
				with urllib.request.urlopen(req) as url:
					data = url.read()
					image_file = io.BytesIO(data)

					im = Image.open(image_file)
					output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
					output.putalpha(mask)

					orig.paste(output, (avatar_locations[id-1][0],avatar_locations[id-1][1]), output)

			draw = ImageDraw.Draw(orig)
			w, h = draw.textsize(member.name)
			draw.text((column_locations[id-1][0]-w/2,column_locations[id-1][1]+h*2), member.name, fill="black")
			utext = "{0:.2f}".format(user[1])
			w, h = draw.textsize(utext)
			draw.text((column_locations[id-1][0]-w/2,column_locations[id-1][1]-h/2), utext, fill="black")
		orig.save('temp.png')
		yield from client.send_file(msg.channel,'temp.png')



					