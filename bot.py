import discord
import asyncio

client = discord.Client()

@client.event
@asyncio.coroutine
def on_message(message):
    # we do not want the bot to reply to itself
    print(message.content)
    if message.author == client.user:
        return
    print(message.content.startswith("!hello"))

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        yield from client.send_message(message.channel, msg)

@client.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run('MTY4Mjg3NzM5Mzg3NTc2MzIw.Ceqg8g.Iza6GzBqdz_iTjYETle3G1codcM')
