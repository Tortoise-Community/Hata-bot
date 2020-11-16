import random
import os
from typing import List, Set, cast
from types import ModuleType
from PIL import Image
from hata import ReuBytesIO, Color, Embed
from config import CLIENT_INFO

from hata.discord import Message, MessageIterator, CLIENTS
from hata.ext.commands.command import checks


from config import MapleClient


clearing: Set[int] = set()

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
				img = Image.new('RGB', (150, 150), color=Color(int(message.content, base=16)).as_tuple)
				img.save(buffer, 'png')
				buffer.seek(0)
				await client.message_create(message.channel, file=('color.png', buffer))
			img = Image.new('RGB', (150, 150), color=message.content)
			img.save(buffer, 'png')
			buffer.seek(0)
			await client.message_create(message.channel, file=('color.png', buffer))
	except:
		return

async def cleartext(client: MapleClient, message: Message):
	"""Clear all text in current channel"""
	# If command has already been responded to, return
	if message.channel.id in clearing:
		return
	clearing.add(message.channel.id)

	try:
		with client.keep_typing(message.channel):
			info = cast(Message, await client.message_create(message.channel, 'Collecting messages...'))
			messages: List[Message] = []
			async for history_message in MessageIterator(client, message.channel):
				messages.append(history_message)
			await client.message_edit(info, f'Deleting {len(messages)} messages')
			await client.message_delete_multiple(messages)
	finally:
		clearing.remove(message.channel.id)

"""Ping command, gets the latency in ms."""
async def ping(client: MapleClient, message: Message):
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
