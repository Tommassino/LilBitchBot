import json
import os.path
import operator

class StringReply(object):
	def __init__(self, message):
		self.message=message
    
	def __call__(self, orig_message, match): 
		msg = self.message.format(orig_message)
		return msg
    
class UserIncrement(object):
	def __init__(self, user_dict):
		self.user_dict=user_dict

	def __call__(self, orig_message, match):
		dict=self.user_dict
		author=orig_message.author.name+':'+orig_message.author.id
		if author not in dict:
			dict[author]=0
		dict[author]=dict[author]+1
		return None

class ListTop(object):
	def __init__(self, dict, top):
		self.dict=dict
		self.top=top

	def __call__(self, msg, mc):
		sorted_dict = sorted(self.dict.items(), key=operator.itemgetter(1))
		message = 'The top lil bitches:'
		for i in range(0, min(len(self.dict),self.top)):
			item = sorted_dict[i]
			message=message+"\n{0}: {1}".format(item[0].split(':')[0],item[1])
		return message
		
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
		
