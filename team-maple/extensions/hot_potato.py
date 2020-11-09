import time
import random
from typing import TypedDict, Optional, Any
from types import ModuleType

from hata.discord import KOKORO, CLIENTS, Message, Guild, Color, Embed, EmbedFooter, ChannelText
from hata.ext.commands import checks, Converter, ConverterFlag
from hata.backend import Lock, sleep


from config import MapleClient


POTATO_DURATION = 15
POTATO_UPDATE_RATE = 2.5
POTATO_TOSS_MIN = 1.5
POTATO_TOSS_MAX = 5

# The currently active hot potato
ActivePotato = TypedDict('ActivePotato', {
	'channel': ChannelText,
	'exploding_at': float,
	'client': MapleClient,
	'message': Message
})
active_potato: Optional[ActivePotato] = None
potato_lock = Lock(KOKORO)


# TODO - ensure guild always exists - if used in DMs,
# guild must be provided, otherwise allow guild to be optional and use message guild
async def potato(
	client: MapleClient,
	message: Message,
	guild: Converter(Guild, ConverterFlag.guild_default, default_code='message.guild')
) -> Any:
	"""Start a game of start potato

	Uses the current or provided guild.
	"""
	global active_potato
	await client.typing(message.channel)

	# Prevent spawning if there's already a hot potato active
	if active_potato:
		return await client.message_create(message.channel, 'Potato already in play')

	# Get client with provided guild
	if guild != message.guild:
		other_client = next((other_client for other_client in CLIENTS if other_client.potato_channel.guild == guild), None)
		if not other_client:
			return await client.message_create(message.channel, 'Guild is not playing hot potato')
	else:
		other_client = client

	channel = other_client.potato_channel

	exploding_at = time.time() + POTATO_DURATION

	potato_msg = await other_client.message_create(channel, embed=build_potato_embed(exploding_at))
	assert potato_msg

	active_potato = {
		'channel': channel,
		'exploding_at': exploding_at,
		'client': other_client,
		'message': potato_msg
	}
	return KOKORO.create_task(potato_countdown())


async def potato_countdown():
	"""Wait to explode potato"""
	global active_potato
	assert active_potato

	# Update message every POTATO_UPDATE_RATE, or don't if it's not set
	if POTATO_UPDATE_RATE:
		exploding_at = active_potato['exploding_at']
		while time.time() < exploding_at:
			await sleep(POTATO_UPDATE_RATE)
			async with potato_lock:
				# TODO - handle if the potato message gets deleted
				await active_potato['client'].message_edit(
					active_potato['message'],
					embed=build_potato_embed(active_potato['exploding_at'])
				)
	else:
		await sleep(active_potato['exploding_at'] - time.time())

	assert active_potato
	await active_potato['client'].message_edit(active_potato['message'], 'Potato Exploded!', embed=None)
	active_potato = None


async def toss(client: MapleClient, message: Message) -> Any:
	"""Toss hot potato from current guild to another one"""
	global active_potato
	await client.typing(message.channel)

	# Don't toss if there is no active potato or the potato is not in the current channel
	if not active_potato or active_potato['channel'] != message.channel:
		return await client.message_create(message.channel, 'There is no potato here')
	if active_potato['exploding_at'] < time.time():
		return await client.message_create(message.channel, 'Potato *just* exploded!')

	# Send potato to any other potato channel, but prefer channels not in the current guild
	async with potato_lock:
		pool = [other_client for other_client in CLIENTS if other_client.potato_channel != message.channel]
		# TODO - guard against channel.guild being None
		foreign_pool = [other_client for other_client in pool if other_client.potato_channel.guild != message.channel.guild]
		if foreign_pool:
			pool = foreign_pool
		other_client = random.choice(pool)

		channel = other_client.potato_channel

		active_potato['channel'] = channel
		active_potato['client'] = other_client

		potato_msg = await other_client.message_create(channel, embed=build_potato_embed(active_potato['exploding_at']))
		assert potato_msg

		# Store and delete after assigning new message in case potato is about to explode
		old_potato_msg = active_potato['message']
		active_potato['message'] = potato_msg
		active_potato['client'] = other_client

		await client.message_delete(old_potato_msg)


def build_potato_embed(exploding_at: float) -> Embed:
	"""Build potato message embed

	Args:
			exploding_at (float): When the potato was created

	Returns:
			Embed: Potato message embed
	"""
	embed = Embed(
		'Hot Potato',
		'You have the hot potato, which only has '
		'{:.2f} seconds before it explodes!'
		.format(exploding_at - time.time())
	)
	embed.footer = EmbedFooter('Use `.toss` to get rid of it!')
	embed.color = Color.from_html('#B79268')
	return embed


async def message_create(client: MapleClient, message: Message):
	if not message.embeds:
		return

	if message.embeds[0].title == 'Hot Potato':
		other_client = next(other_client for other_client in CLIENTS if other_client.potato_channel == message.channel)
		if client == other_client:
			return

		await sleep(random.uniform(POTATO_TOSS_MIN, POTATO_TOSS_MAX))
		# If the potato has exploded or changed message, don't toss
		if not active_potato or active_potato['message'].id != message.id:
			return

		await client.typing(message.channel)
		msg = await client.message_create(message.channel, '.toss')

		await other_client.command_processer.commands['toss'](other_client, msg, '')


def setup(_: ModuleType):
	for client in CLIENTS:
		client.events(message_create)

		potato_channel_check = checks.is_channel(client.potato_channel)
		client.commands(checks=[potato_channel_check])(toss)
		client.commands(checks=[potato_channel_check])(potato)
