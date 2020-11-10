import random
import math
from typing import List, cast, Optional
from types import ModuleType


from hata.discord import Message, CLIENTS
from hata.discord.emoji import BUILTIN_EMOJIS
from hata.ext.commands import utils


from config import MapleClient


GUESS_WAIT_TIMEOUT = 15


def is_msg_numeric(msg: Message):
	try:
		int(msg.content)
		return True
	except ValueError:
		return False


guessing = set()


async def message_create(client: MapleClient, message: Message):
	if (
		message.id in guessing
		or client.id == message.author.id
		or not message.content.lower().startswith("i'm thinking of a number between")
	):
		return
	guessing.add(message.id)

	lowest, highest = [
		int(part.strip())
		for part in message.content.split('between')[1].strip().split(' and ')
	]
	attempted = []
	try:
		while True:
			trying = lowest + math.ceil((highest - lowest) / 2)
			if attempted and attempted[-1] == trying:
				trying -= 1
			attempted.append(trying)

			await client.human_delay(message.channel)
			await client.message_create(message.channel, str(trying))
			msg = await utils.wait_for_message(
				client,
				message.channel,
				lambda msg: msg.author.id == message.author.id,
				GUESS_WAIT_TIMEOUT
			)
			if 'guessed' in msg.content.lower():
				break

			if 'low' in msg.content.lower():
				lowest = attempted[-1]
			elif 'high' in msg.content.lower():
				highest = attempted[-1]

		await client.reaction_add(msg, BUILTIN_EMOJIS['fireworks'])
	except TimeoutError:
		await client.message_create(message.channel, "Guess I'll never know what the number was...")
	finally:
		guessing.remove(message.id)


telling = set()


async def guess_number(client: MapleClient, message: Message, lowest: int = 1, highest: int = 10):
	if message.id in telling:
		return
	telling.add(message.id)
	number = random.randint(lowest, highest)
	await client.message_create(
		message.channel,
		"I'm thinking of a number between {} and {}".format(lowest, highest)
	)

	try:
		guesses = {}
		while True:
			msg = await utils.wait_for_message(client, message.channel, is_msg_numeric, GUESS_WAIT_TIMEOUT)
			guesses[msg.author.id] = guesses.get(msg.author.id, 0) + 1
			guess = int(msg.content)
			if guess == number:
				break

			await client.human_delay(message.channel)
			await client.message_create(
				message.channel,
				'Too {}'.format('High' if guess > number else 'Low')
			)

		await client.human_delay(message.channel)
		await client.message_create(
			message.channel,
			'{:m} guessed my number in {} guesses!'.format(
				msg.author,
				guesses[msg.author.id]
			)
		)
	except TimeoutError:
		await client.message_create(message.channel, 'Well the number was {}'.format(number))
	finally:
		telling.remove(message.id)


def setup(_: ModuleType):
	for client in CLIENTS:
		client.events(message_create)
		client.commands(guess_number)
