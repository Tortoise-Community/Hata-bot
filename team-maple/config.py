import os
import random
import sys
from typing import List, Optional, TYPE_CHECKING


from dotenv import load_dotenv
from hata.discord import Client, ChannelText
from hata.discord.parsers import EventDescriptor, _EventHandlerManager
from hata.ext.commands import setup_ext_commands, CommandProcesser
from hata.backend import KeepType, sleep

from env import CLIENT_INFO, ClientInfoDict
load_dotenv()


# When delaying, the least and most amount of seconds to wait to appear human
HUMAN_DELAY_RANGE = (1, 2)


# Required to make type checkers happy
if TYPE_CHECKING:
	class MapleClient(Client):
		command_processer: CommandProcesser
		commands: _EventHandlerManager
		events: EventDescriptor
		potato_channel: ChannelText

		def _init(self, potato_channel: ChannelText) -> 'MapleClient':
			...

		async def human_delay(self, channel: Optional[ChannelText] = ...) -> None:
			...
else:
	@KeepType(Client)
	class MapleClient:
		def _init(self, potato_channel):
			self.potato_channel = potato_channel
			return self

		async def human_delay(self, channel=None):
			if channel:
				await self.typing(channel)

			await sleep(random.uniform(*HUMAN_DELAY_RANGE))


def create_clients() -> None:
	"""Create all clients

	First attempt to load data from enviroment variables, then the env.py file
	"""
	client_tokens = [token.strip() for token in (os.getenv('CLIENT_TOKENS') or '').split(',') if token]

	if not CLIENT_INFO and not client_tokens:
		print('No clients found in enviroment variables or env.py')
		sys.exit(1)

	client_info: List[ClientInfoDict] = []
	if not client_tokens:
		client_info = CLIENT_INFO
	else:
		client_ids = [
			int(id.strip())
			for id in (os.getenv('CLIENT_IDS') or '').split(',')
			if id
		]
		potato_channel_ids = [
			int(id.strip())
			for id in (os.getenv('POTATO_CHANNEL_IDS') or '').split(',')
			if id.strip()
		]
		for i, token in enumerate(client_tokens):
			client_info.append({
				'ID': client_ids[i],
				'TOKEN': token,
				'POTATO_CHANNEL_ID': potato_channel_ids[i]
			})

	print('Attemping to create {} MapleClients...'.format(len(client_info)))
	for info in client_info:
		potato_channel = ChannelText.precreate(info['POTATO_CHANNEL_ID'])
		client = MapleClient(info['TOKEN'], client_id=info['ID'])._init(potato_channel)
		# TODO - parameterize prefix
		setup_ext_commands(client, '.')
