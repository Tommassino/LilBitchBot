import discord
import re
import asyncio
import glob
import os.path  
import subprocess
import io

class Module(object):
	def __init__(self, wrapper):
		self.logger = wrapper.logger
		self.wrapper = wrapper
		self.audio_lengths = {}
		self.messageHooks = {
			re.compile('^!join .*'): JoinVoice('!join',self),
			re.compile('^!play .*'): PlaySound('!play',self, wrapper, 0.2),
			re.compile('^!list'): ListVoice('!play',self),
			re.compile('^!length .*'): ListDuration('!length',self)
		}

		
	def poll_length(self, audio_name):
		if audio_name in self.audio_lengths:
			return self.audio_lengths[audio_name]
		files = glob.glob("./audio/"+audio_name.strip()+".*")
		file = files[0] #could throw warning if there are more than one
		try:
			p = subprocess.Popen(["avconv" , "-i" , file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			out, err = p.communicate()
			retcode = p.wait()
		except e:
			pass
		err=err.decode("utf-8")
		reg = re.compile("Duration: (.*),")
		match = reg.search(err)
		duration = match.group(1).split('.')[0]
		splits = duration.split(':')
		seconds = int(splits[2])+int(splits[1])*60+int(splits[0])*3600
		self.audio_lengths[audio_name]=seconds
		return seconds
		
class JoinVoice(object):
	def __init__(self, cmd, module):
		self.cmd=cmd
		self.module=module

	def __call__(self, msg, mtc, cli):
		if cli.is_voice_connected(msg.server):
			yield from cli.voice.disconnect()
		channel_name=msg.content[len(self.cmd):].strip()
		check = lambda c: c.name == channel_name and c.type == discord.ChannelType.voice
		channel = discord.utils.find(check,msg.server.channels)
		if channel is None:
			yield from cli.send_message(msg.channel,"Invalid channel name")
			return
		yield from cli.join_voice_channel(channel)


class ListDuration(object):
	def __init__(self, cmd, module):
		self.cmd=cmd
		self.module=module
	
	def __call__(self,msg,mtc,cli):  
		yield from cli.send_message(msg.channel,"{0} seconds".format(self.module.poll_length(msg.content[len(self.cmd):].strip())))

class ListVoice(object):
	def __init__(self, cmd, module):
		self.cmd=cmd
		self.module=module

	def __call__(self, msg, mtc, cli):
		files = glob.glob("./audio/*")
		names = []
		for file in files:
			names.append(os.path.basename(file))
		s = ", ".join(names)
		yield from cli.send_message(msg.channel, "Available sounds: {0}".format(s))
		

class PlaySound(object):
	def __init__(self, cmd, module, wrapper, play_cost):
		self.cmd=cmd
		self.module=module
		self.player=None
		self.wrapper = wrapper
		self.play_cost = play_cost
		self.extensions = [".wav",".mp3"]

	def __call__(self, msg, mtc, cli):
		coins = self.wrapper.money.get_points(msg.author.id)
		if not coins:
			coins = 0
		else:
			coins=coins[0]
		audio_name=msg.content[len(self.cmd):].strip()
		duration = self.module.poll_length(audio_name)
		cost = duration*self.play_cost
		if coins < cost:
			yield from cli.send_message(msg.channel, "Fuck off, not enough lil bitch credit (got {0:.2f}, need {1})!".format(coins,cost))
			return
		if not cli.is_voice_connected(msg.server):
			yield from cli.send_message(msg.channel, "Cant play if im not in a voice channel, use !join to tell me where to play.")
			return
		files = glob.glob("./audio/"+audio_name+".*")
		if len(files)==0:
			yield from cli.send_message(msg.channel, "Cant find that audio file, sorry man... :(")
			return
		file = files[0] #could throw warning if there are more than one
		extension = os.path.splitext(file)[1]
		print(extension)
		if extension not in self.extensions:
			yield from cli.send_message(msg.channel, "The audio file found has a unsupported extension, sorry man... :(")
			return
		if not self.player or self.player.is_done():
			print("Playing audio file {0}".format(file))
			self.wrapper.money.add_points(msg.author.id, -cost)
			self.player = cli.voice_client_in(msg.server).create_ffmpeg_player(file)
			self.player.start()

