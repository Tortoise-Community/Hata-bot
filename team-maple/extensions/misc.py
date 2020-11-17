from PIL import Image
from typing import List, Set, cast
from types import ModuleType


from hata.discord import Message, MessageIterator, Color, Embed, CLIENTS
from hata.backend import ReuBytesIO
from hata.ext.commands.command import checks


from config import MapleClient, CLIENT_INFO


Inosuke = CLIENTS[CLIENT_INFO[0]['ID']]
Zenitsu = CLIENTS[CLIENT_INFO[1]['ID']]

@Inosuke.events
async def message_create(client, message):
	if message.author is client or message.author is Zenitsu:
		return

# Simple feature which sends the picture of the color mentioned in the message
	try:
		with ReuBytesIO() as buffer:
			if len(message.content) == 8 and message.content.lower().startswith('0x'):
				img = Image.new('RGBA', (150, 150), color=Color(int(message.content, base=16)).as_tuple)
				img.save(buffer, 'png')
				buffer.seek(0)
				await client.message_create(message.channel, file=('color.png', buffer))
			img = Image.new('RGBA', (150, 150), color=message.content)
			img.save(buffer, 'png')
			buffer.seek(0)
			await client.message_create(message.channel, file=('color.png', buffer))
	except:
		return


clearing: Set[int] = set()


async def cleartext(client: MapleClient, message: Message):
	"""Delete all non-pinned messages in the current channel"""
	# If channel is already being cleared, return
	if message.channel.id in clearing:
		return
	clearing.add(message.channel.id)

	try:
		with client.keep_typing(message.channel):
			info = cast(Message, await client.message_create(message.channel, 'Collecting messages...'))
			messages: List[Message] = []
			async for history_message in MessageIterator(client, message.channel):
				if history_message.pinned:
					continue
				messages.append(history_message)
			await client.message_edit(info, f'Deleting {len(messages)} messages')
			await client.message_delete_multiple(messages)
	finally:
		clearing.remove(message.channel.id)


async def ping(client: MapleClient, message: Message):
	"""Gets the latency in ms."""
	embed = Embed(title='Pong! 🏓', description=f'Ping is {round(client.gateway.latency * 1000)} ms')
	await client.message_create(message.channel, embed=embed)


def setup(_: ModuleType):
	for client in CLIENTS:
		client.commands(checks=[checks.owner_only()])(cleartext)
		client.commands()(ping)


def teardown(_: ModuleType):
	for client in CLIENTS:
		client.commands.remove(cleartext)
		client.commands.remove(ping)
