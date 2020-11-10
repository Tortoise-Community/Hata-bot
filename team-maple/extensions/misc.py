from typing import List, Set, cast
from types import ModuleType


from hata.discord import Message, MessageIterator, CLIENTS


from config import MapleClient


clearing: Set[int] = set()


async def cleartext(client: MapleClient, message: Message):
	"""Clear all text in current channel"""
	# If command has already been responded to, return
	if message.id in clearing:
		return
	clearing.add(message.id)

	with client.keep_typing(message.channel):
		info = cast(Message, await client.message_create(message.channel, 'Collecting messages...'))
		messages: List[Message] = []
		async for history_message in MessageIterator(client, message.channel):
			messages.append(history_message)
		await client.message_edit(info, f'Deleting {len(messages)} messages')
		await client.message_delete_multiple(messages)

	clearing.remove(message.id)


def setup(_: ModuleType):
	for client in CLIENTS:
		client.commands(cleartext)
