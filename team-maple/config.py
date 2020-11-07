import os
from typing import TypedDict, Dict, List


from dotenv import load_dotenv
load_dotenv()
from hata.discord import Client, ChannelText
from hata.ext.commands import setup_ext_commands


ClientInfoDict = TypedDict('ClientInfoDict', {
	'POTATO_CHANNEL': ChannelText,
	'CLIENT': Client
})

def load_client_info() -> Dict[int, ClientInfoDict]:
	"""Create all clients and generate information dicts

	Returns:
			Dict[int, ClientInfoDict]: Mapping of client information dicts
	"""
	# TODO - implement error handling based on missing or invalid enviroment values
	client_ids = [int(token.strip()) for token in (os.getenv('CLIENT_IDS') or '').split(',') if token]
	client_tokens = [token.strip() for token in (os.getenv('CLIENT_TOKENS') or '').split(',') if token]
	potato_channels: List[ChannelText] = [ChannelText.precreate(int(id.strip())) for id in (os.getenv('POTATO_CHANNEL_IDS') or '').split(',') if id.strip()]

	info: Dict[int, ClientInfoDict] = {}

	for i, token in enumerate(client_tokens):
		client = Client(token, client_id=client_ids[i])
		info[client_ids[i]] = {
			'POTATO_CHANNEL': potato_channels[i],
			'CLIENT': client
		}
		# TODO - parameterize prefix
		setup_ext_commands(client, '.')

	return info

CLIENT_INFO = load_client_info()
