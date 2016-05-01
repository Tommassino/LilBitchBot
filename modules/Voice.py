import discord
import re
import asyncio

class Module(object):
	def __init__(self, wrapper):
		self.voice = None
		self.wrapper = wrapper
		self.messageHooks = {
			re.compile('^!join .*'): JoinVoice('!join',self),
			re.compile('^!play .*'): PlaySound('!play',self, wrapper, 0.25)
		}

class JoinVoice(object):
	def __init__(self, cmd, module):
		self.cmd=cmd
		self.module=module

	def __call__(self, msg, mtc, cli):
		
		channel_name=msg.content[len(self.cmd):].strip()
		check = lambda c: c.name == channel_name and c.type == discord.ChannelType.voice
		channel = discord.utils.find(check,msg.server.channels)
		if channel is None:
			yield from cli.send_message(msg.channel,"Invalid channel name")
			return
		self.module.voice = yield from cli.join_voice_channel(channel)

class PlaySound(object):
	def __init__(self, cmd, module, wrapper, play_cost):
		self.cmd=cmd
		self.module=module
		self.player=None
		self.wrapper = wrapper
		self.play_cost = play_cost

	def __call__(self, msg, mtc, cli):
		global voiceChannel
		coins = self.wrapper.money.get_money(msg.author)
		if coins < self.play_cost:
			yield from cli.send_message(msg.channel,"Fuck off, not enough lil bitch credit!")
			return
		if not self.player or self.player.is_done():
			self.wrapper.money.add_money(msg.author, -self.play_cost)
			file = "audio/"+msg.content[len(self.cmd):].strip()+".wav"
			self.player = self.module.voice.create_ffmpeg_player(file)
			self.player.start()
