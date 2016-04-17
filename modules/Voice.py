import discord
import re
import asyncio

class Module(object):
	def __init__(self):
		self.voice = None

	def register(client):
		client.messageHooks[re.compile('^!join .*')] = JoinVoice('!join',self)
		client.messageHooks[re.compile('^!play .*')] = PlaySound('!play',self)

class JoinVoice(object):
	def __init__(self,cmd,module):
		self.cmd=cmd
		self.module=module

	def __call__(self,msg,mtc,cli):
		
		channel_name=msg.content[len(self.cmd):].strip()
		check = lambda c: c.name == channel_name and c.type == discord.ChannelType.voice
		channel = discord.utils.find(check,msg.server.channels)
		if channel is None:
			yield from cli.send_message(msg.channel,"Invalid channel name")
			return
		self.module.voice = yield from cli.join_voice_channel(channel)

class PlaySound(object):
	def __init__(self,cmd,module):
		self.cmd=cmd
		self.module=module8

	def __call__(self,msg,mtc,cli):
		global voiceChannel
		file = msg.content[len(self.cmd):].strip()+".wav"
		player = self.module.voice.create_ffmpeg_player(file)
		player.start()