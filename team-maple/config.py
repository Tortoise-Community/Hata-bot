import os
from typing import List


from dotenv import load_dotenv
from hata.discord import Client, ChannelText
from hata.ext.commands import setup_ext_commands
from hata.backend import KeepType

load_dotenv()


@KeepType(Client)
class MapleClient:
	def _init(self, potato_channel: ChannelText):
		self.potato_channel = potato_channel
		return self


def create_clients() -> None:
	"""Create all clients"""
	# TODO - implement error handling based on missing or invalid enviroment values
	client_ids = [int(token.strip()) for token in (os.getenv('CLIENT_IDS') or '').split(',') if token]
	client_tokens = [token.strip() for token in (os.getenv('CLIENT_TOKENS') or '').split(',') if token]
	potato_channels: List[ChannelText] = [
		ChannelText.precreate(int(id.strip()))
		for id in (os.getenv('POTATO_CHANNEL_IDS') or '').split(',')
		if id.strip()
	]

	for i, token in enumerate(client_tokens):
		client = MapleClient(token, client_id=client_ids[i])._init(potato_channels[i])
		# TODO - parameterize prefix
		setup_ext_commands(client, '.')
