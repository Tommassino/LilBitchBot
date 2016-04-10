import discord
import asyncio
import re
import model

client = discord.Client()

handles = {
  re.compile('^!hello$'): model.StringReply('Hello {0.author.mention}')  
}

@client.event
@asyncio.coroutine
def on_message(message):
	# we do not want the bot to reply to itself
	if message.author == client.user:
		return

	for regexp in handles:
		match = regexp.match(message.content)
		if match:
			msg = handles[regexp](message,match)
			yield from client.send_message(message.channel, msg)

#    if message.content.startswith('!hello'):
#        msg = 'Hello {0.author.mention}'.format(message)
#        yield from client.send_message(message.channel, msg)

@client.event
@asyncio.coroutine
def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')

client.run('MTY4Mjg3NzM5Mzg3NTc2MzIw.Ceqg8g.Iza6GzBqdz_iTjYETle3G1codcM')
