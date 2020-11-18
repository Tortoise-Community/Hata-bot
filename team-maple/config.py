import os
import random
import sys
from typing import List, Tuple, Optional, TYPE_CHECKING


from dotenv import load_dotenv
from hata.discord import Client, ChannelText
from hata.discord.parsers import EventDescriptor, _EventHandlerManager
from hata.ext.commands import setup_ext_commands, CommandProcesser
from hata.backend import KeepType, sleep

from env import PREFIX, CLIENT_INFO, CHATBOT_API, ClientInfoDict
load_dotenv()


# When delaying, the least and most amount of seconds to wait to appear human
HUMAN_DELAY_RANGE = (1, 2)


# Required to make type checkers happy
if TYPE_CHECKING:
	class MapleClient(Client):
		command_processer: CommandProcesser
		commands: _EventHandlerManager
		events: EventDescriptor
		potato_channel: Optional[ChannelText]

		def _init(self, potato_channel: Optional[ChannelText] = ...) -> 'MapleClient':
			...

		async def human_delay(self, channel: Optional[ChannelText] = ...) -> None:
			...
else:
	@KeepType(Client)
	class MapleClient:
		def _init(self, potato_channel=None):
			self.potato_channel = potato_channel
			return self

		async def human_delay(self, channel=None):
			if channel:
				await self.typing(channel)

			await sleep(random.uniform(*HUMAN_DELAY_RANGE))

def load_client_info() -> Tuple[List[ClientInfoDict], str]:
	"""First attempt to load data from enviroment variables, then the env.py file"""
	client_tokens = [token.strip() for token in (os.getenv('CLIENT_TOKENS') or '').split(',') if token]

	chatbot_api = os.getenv('CHATBOT_API') or CHATBOT_API

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
		if len(client_tokens) != len(client_ids):
			print('Number of Client IDs and Tokens must be equal')
			sys.exit(1)

		potato_channel_ids = [
			int(id.strip())
			for id in (os.getenv('POTATO_CHANNEL_IDS') or '').split(',')
			if id.strip()
		]
		client_prefix = os.getenv('CLIENT_PREFIX') or PREFIX
		client_prefixes = [
			prefix.strip()
			for prefix in (os.getenv('CLIENT_PREFIXES') or '').split(',')
			if prefix.strip()
		]
		for i, token in enumerate(client_tokens):
			client_info.append({
				'ID': client_ids[i],
				'TOKEN': token,
				'PREFIX': client_prefixes[i] if len(client_prefixes) >= i + 1 else client_prefix,
				'POTATO_CHANNEL_ID': potato_channel_ids[i] if len(potato_channel_ids) >= i + 1 else None,
			})

	return client_info, chatbot_api

CLIENT_INFO, CHATBOT_API = load_client_info()

def create_clients() -> None:
	"""Create all clients"""
	print('Attemping to create {} MapleClients...'.format(len(CLIENT_INFO)))
	for info in CLIENT_INFO:
		potato_channel = ChannelText.precreate(info['POTATO_CHANNEL_ID']) if 'POTATO_CHANNEL_ID' in info else None
		client = MapleClient(info['TOKEN'], client_id=info['ID'])._init(potato_channel)
		setup_ext_commands(client, info['PREFIX'] if 'PREFIX' in info else PREFIX)
