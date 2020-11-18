import functools
from typing import Any, Callable, Set, Dict, Optional


from hata.discord import Message, EventWaitforBase, Client, KOKORO, ChannelBase
from hata.backend import Future
from hata.ext.commands import WaitAndContinue, checks


from config import MapleClient




def make_exclusive_event(func: Callable[[MapleClient, Message, ], Any]):
	"""Make a message-receiving event only execute for the first client"""
	handled: Set[int] = set()

	@functools.wraps(func)
	async def wrapper(client: MapleClient, message: Message, *args: Any):
		if message.id in handled:
			return
		handled.add(message.id)
		try:
			await func(client, message, *args)
		finally:
			handled.remove(message.id)

	return wrapper


class is_exclusive_command(checks._check_base):
	"""Ensure command message is only executed by one client"""
	handled: Dict[int, int] = {}

	async def __call__(self, client: Client, message: Message):
		cid = self.handled.get(message.id, None)
		if cid == client.id:
			return True
		if cid is not None:
			return False
		self.handled.clear()
		self.handled[message.id] = client.id
		return True


class MessageEditWaitfor(EventWaitforBase):
	__event_name__ = 'message_edit'


def wait_for_message_edit(
	client: Client,
	channel: ChannelBase,
	check: Callable[[Message, Optional[dict]], Any],
	timeout: float
):
	"""Wait for a message_edit event"""
	future = Future(KOKORO)
	WaitAndContinue(future, check, channel, client.events.message_edit, timeout)
	return future
