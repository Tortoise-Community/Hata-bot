from dotenv import load_dotenv
from hata.discord.color import Color
from hata.discord.embed import Embed, EmbedFooter
load_dotenv()

from hata.discord.client_core import KOKORO
from hata.discord import start_clients, stop_clients, Client, Message, ChannelText, MessageIterator
from hata.ext.commands import setup_ext_commands, checks, Converter, ConverterFlag
import hata.ext.asyncio as asyncio


import time
import random
import os
from typing import Optional, TypedDict, Dict, Any, List



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

# The currently active hot potato
ActivePotato = TypedDict('ActivePotato', {
	'channel': ChannelText,
	'exploding_at': float,
	'client': Client,
	'message': Message
})
POTATO_DURATION = 15
POTATO_UPDATE_RATE = 2.5
active_potato: Optional[ActivePotato] = None


async def ready(client: Client):
	# TODO - output info for client
	print(f'{client:f} logged in.')

# TODO - ensure guild always exists - if used in DMs, guild must be provided, otherwise allow guild to be optional and use message guild
async def potato(client: Client, message: Message, guild: Converter(Guild, ConverterFlag.guild_default, default_code='message.guild')) -> Any:
	"""Start a game of start potato

	Uses the current or provided guild.
	"""
	global active_potato
	# Prevent spawning if there's already a hot potato active
	if active_potato:
		return await client.message_create(message.channel, 'Potato already in play')

	# Get client with provided guild
	if guild != message.guild:
		info = next((info for info in CLIENT_INFO.values() if info['POTATO_CHANNEL'].guild == guild), None)
		if not info:
			return await client.message_create(message.channel, 'Guild is not playing hot potato')
	else:
		info = CLIENT_INFO[client.id]

	other_client = info['CLIENT']
	channel = info['POTATO_CHANNEL']


	exploding_at = time.time() + POTATO_DURATION

	potato_msg = await other_client.message_create(channel, embed=build_potato_embed(exploding_at))
	assert potato_msg

	active_potato = {
		'channel': channel,
		'exploding_at': exploding_at,
		'client': other_client,
		'message': potato_msg
	}
	return asyncio.create_task(potato_countdown())

async def potato_countdown():
	"""Wait to explode potato"""
	global active_potato
	assert active_potato

	# Update message every POTATO_UPDATE_RATE, or don't if it's not set
	if POTATO_UPDATE_RATE:
		exploding_at = active_potato['exploding_at']
		while time.time() < exploding_at:
			await asyncio.sleep(POTATO_UPDATE_RATE)
			await active_potato['client'].message_edit(active_potato['message'], embed=build_potato_embed(active_potato['exploding_at']))
	else:
		await asyncio.sleep(active_potato['exploding_at'] - time.time())


	assert active_potato
	await active_potato['client'].message_edit(active_potato['message'], 'Potato Exploded!', embed=None)
	active_potato = None

async def toss(client: Client, message: Message) -> Any:
	"""Toss hot potato from current guild to another one"""
	global active_potato
	# Don't toss if there is no active potato or the potato is not in the current channel
	if not active_potato or active_potato['channel'] != message.channel:
		return await client.message_create(message.channel, 'There is no potato here')
	if active_potato['exploding_at'] < time.time():
		return await client.message_create(message.channel, 'Potato *just* exploded!')

	# Send potato to any other potato channel, but prefer channels not in the current guild
	pool = [info for info in CLIENT_INFO.values() if info['POTATO_CHANNEL'] != message.channel]
	# TODO - guard against channel.guild being None
	foreign_pool = [info for info in pool if info['POTATO_CHANNEL'].guild != message.channel.guild]
	if foreign_pool:
		pool = foreign_pool
	info = random.choice(pool)


	other_client = info['CLIENT']
	channel = info['POTATO_CHANNEL']

	active_potato['channel'] = channel
	active_potato['client'] = other_client

	potato_msg = await other_client.message_create(channel, embed=build_potato_embed(active_potato['exploding_at']))
	assert potato_msg

	# Store and delete after assigning new message in case potato is about to explode
	old_potato_msg = active_potato['message']
	active_potato['message'] = potato_msg

	await client.message_delete(old_potato_msg)

def build_potato_embed(exploding_at: float) -> Embed:
	"""Build potato message embed

	Args:
			exploding_at (float): When the potato was created

	Returns:
			Embed: Potato message embed
	"""
	embed = Embed('Hot Potato', 'You have the hot potato, which only has {:.2f} seconds before it explodes!'.format(exploding_at - time.time()))
	embed.footer = EmbedFooter('Use `.toss` to get rid of it!')
	embed.color = Color.from_html('#B79268')
	return embed


async def message_create(client: Client, message: Message):
	if not message.embeds:
		return

	if message.embeds[0].title == 'Hot Potato':
		info = next(info for info in CLIENT_INFO.values() if info['POTATO_CHANNEL'] == message.channel)
		other_client = info['CLIENT']
		if client == other_client:
			return

		await asyncio.sleep(random.uniform(1.5, 5))
		# If the potato has exploded or changed message, don't toss
		if not active_potato or active_potato['message'].id != message.id:
			return

		msg = await client.message_create(message.channel, '.toss')

		await other_client.command_processer.commands['toss'](other_client, msg, '')

for info in CLIENT_INFO.values():
	client = info['CLIENT']
	client.events(ready)
	# TODO - look into better way to constrain commands in channel
	client.commands(checks=[checks.is_channel(info['POTATO_CHANNEL'])])(toss)
	client.commands(checks=[checks.is_channel(info['POTATO_CHANNEL'])])(potato)

if __name__ == '__main__':
	print('Connecting...')
	start_clients()
	try:
		import time
		time.sleep(2000.5)
	except KeyboardInterrupt:
		stop_clients()
		print('Disconnected')
		KOKORO.stop()