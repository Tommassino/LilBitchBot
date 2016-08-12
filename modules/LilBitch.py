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
		self.admins = wrapper.config['admins']
		self.bitchCounter = wrapper.money
		self.messageHooks = {
			re.compile('.*lil.*bitch.*', flags=re.IGNORECASE): UserIncrement(self.bitchCounter),
			re.compile('.*who.*lil.*bitch.*', flags=re.IGNORECASE): ReplyTop(self.bitchCounter),
			re.compile('^!top$'): ListTop(self.bitchCounter,3),
			re.compile('^am i a lil bitch.*$', flags=re.IGNORECASE): ListBitch(self.bitchCounter),
			re.compile('^!drawTop$', flags=re.IGNORECASE): DrawTop(wrapper.money,3,wrapper),
			re.compile('^!give (.*) (.*)'): Grant(wrapper.money, self)
		}
		self.lastSpendTime = {}
		
def find_member_id(server, user_name):
	for member in server.members:
		if member.name==str(user_name):
			print(member.name)
			return member
	return None
		
def find_member(server, user_id):
	for member in server.members:
		if member.id==str(user_id):
			return member
	return None
	
def get_name(server, user_id):
	member = find_member(server,user_id)
	if member:
		return member.name
	return 'unknown'
	
class Grant(object):
	def __init__(self, money, module):
		self.money=money
		self.module=module

	def __call__(self, msg, match, client):
		if not int(msg.author.id) in self.module.admins:
			return None		
		name=match.group(1)
		points=int(match.group(2))
		user = find_member_id(msg.server, name)
		if user:
			self.money.add_points(user.id, points)
			yield from client.send_message(msg.channel,"Granted user {0} {1} lil bitches!".format(name, points))
		else:
			yield from client.send_message(msg.channel,"Cannot find user {0}!".format(name))
		return None

class UserIncrement(object):
	def __init__(self, user_db):
		self.user_db=user_db
		self.timeout_dict={}
		self.timeout=10

	def __call__(self, msg, match,client):
		tm=time.time()
		if msg.author.id in self.timeout_dict and tm-self.timeout_dict[msg.author.id] < 10:
			return None
		self.timeout_dict[msg.author.id]=tm
		self.user_db.add_points(msg.author.id, 1)
		return None

class ListBitch(object):
	def __init__(self, user_db):
		self.user_db=user_db

	def __call__(self, msg, mc, cl):
		count=self.user_db.get_points(msg.author.id)
		if count:
			yield from cl.send_message(msg.channel,"You have {0} lil bitches!".format(count[0]))

class ListTop(object):
	def __init__(self, user_db, top):
		self.user_db=user_db
		self.top=top

	def __call__(self, msg, mc,client):
		top_users = self.user_db.get_top(self.top)
		print(top_users)
		message = 'The top lil bitches:'
		for i in range(0, len(top_users)):
			item = top_users[i]
			name = get_name(msg.server,item[0])
			message=message+"\n{0}: {1:.2f}".format(name,item[1])
		yield from client.send_message(msg.channel,message)

class ReplyTop(object):
	def __init__(self, user_db):
		self.user_db=user_db

	def __call__(self,msg,mc,client):
		top_user = self.user_db.get_top(1)
		if len(top_user)>0:
			top = top_user[0]               
			name = get_name(msg.server,top[0])
			yield from client.send_message(msg.channel,"{0} is a lil bitch!".format(name))

class DrawTop(object):
	def __init__(self, user_db, top, wrapper):
		self.user_db=user_db
		self.top=top
		self.wrapper=wrapper

	def find_member(self, members, user_id):
		for member in members:
			if member.id==str(user_id):
				return member
		return None
	
	def __call__(self,msg,mc,client):
		top_users = self.user_db.get_top(self.top)
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



					