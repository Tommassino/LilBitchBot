import discord
import re
import asyncio
import glob
import os.path

class Module(object):
	def __init__(self, wrapper):
		self.wrapper = wrapper
		self.messageHooks = {
			re.compile('^!join .*'): JoinVoice('!join',self),
			re.compile('^!play .*'): PlaySound('!play',self, wrapper, 0.25),
			re.compile('^!list'): ListVoice('!play',self)
		}

class JoinVoice(object):
	def __init__(self, cmd, module):
		self.cmd=cmd
		self.module=module

	def __call__(self, msg, mtc, cli):
		if cli.voice:
			yield from cli.voice.disconnect()
		channel_name=msg.content[len(self.cmd):].strip()
		check = lambda c: c.name == channel_name and c.type == discord.ChannelType.voice
		channel = discord.utils.find(check,msg.server.channels)
		if channel is None:
			yield from cli.send_message(msg.channel,"Invalid channel name")
			return
		yield from cli.join_voice_channel(channel)
		

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
		coins = self.wrapper.money.get_money(msg.author)
		if coins < self.play_cost:
			yield from cli.send_message(msg.channel, "Fuck off, not enough lil bitch credit!")
			return
		if not cli.voice:
			yield from cli.send_message(msg.channel, "Cant play if im not in a voice channel, use !join to tell me where to play.")
			return
		files = glob.glob("./audio/"+msg.content[len(self.cmd):].strip()+".*")
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
			self.wrapper.money.add_money(msg.author, -self.play_cost)
			self.player = cli.voice.create_ffmpeg_player(file)
			self.player.start()
