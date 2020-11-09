from typing import List, cast, TYPE_CHECKING
from types import ModuleType


from hata.discord import Client, Message, MessageIterator


if TYPE_CHECKING:
	from config import CLIENT_INFO



clearing = set()

async def cleartext(client: Client, message: Message):
	"""Clear all text in current channel"""
	if message.id in clearing:
		return

	with client.keep_typing(message.channel):
		clearing.add(message.id)

		info = cast(Message, await client.message_create(message.channel, 'Collecting messages...'))
		messages: List[Message] = []
		async for history_message in MessageIterator(client, message.channel):
			messages.append(history_message)
		await client.message_edit(info, f'Deleting {len(messages)} messages')
		await client.message_delete_multiple(messages)

		clearing.remove(message.id)

def setup(_: ModuleType):
	for info in CLIENT_INFO.values():
		info['CLIENT'].commands(cleartext)
