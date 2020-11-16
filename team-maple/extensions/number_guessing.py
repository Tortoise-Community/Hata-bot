import random
import math
from typing import List, Set, Dict
from types import ModuleType


from hata.discord import Message, CLIENTS
from hata.discord.emoji import BUILTIN_EMOJIS
from hata.ext.commands import utils


from config import MapleClient


GUESS_WAIT_TIMEOUT = 15

START_TEMPLATE = ["I'm thinking of a number between ", " and "]
INCORRECT_TEMPLATE = 'Too {}'
CORRECT_TEMPLATE = '{:m} guessed my number in {} guesses!'

TOO_LOW_KEYWORD = 'low'
TOO_HIGH_KEYWORD = 'high'
CORRECT_KEYWORD = 'guessed'


def is_msg_numeric(msg: Message):
	try:
		int(msg.content)
		return True
	except ValueError:
		return False


guessing: Set[int] = set()


async def message_create(client: MapleClient, message: Message):
	# Stop if number already being guessed, is self, or not a number guessing prompt
	if (
		message.id in guessing
		or client.id == message.author.id
		or not message.content.lower().startswith(START_TEMPLATE[0].lower())
	):
		return
	guessing.add(message.id)

	lowest, highest = [
		int(part.strip())
		for part in (
			message.content.lower()
			.split(START_TEMPLATE[0].lower())[1].strip()
			.split(START_TEMPLATE[1].lower())
		)
	]
	# List of tried numbers
	attempted: List[int] = []
	try:
		while True:
			# Calculate next number to try
			trying = lowest + math.ceil((highest - lowest) / 2)
			if attempted and attempted[-1] == trying:
				trying -= 1
			attempted.append(trying)

			# Send next number, and wait for response from prompt author
			await client.human_delay(message.channel)
			await client.message_create(message.channel, str(trying))
			msg = await utils.wait_for_message(
				client,
				message.channel,
				lambda msg: msg.author.id == message.author.id,
				GUESS_WAIT_TIMEOUT
			)
			# Break if correct
			if CORRECT_KEYWORD.lower() in msg.content.lower():
				break
			# Otherwise update lowest/highest value
			elif TOO_LOW_KEYWORD.lower() in msg.content.lower():
				lowest = attempted[-1]
			elif TOO_HIGH_KEYWORD.lower() in msg.content.lower():
				highest = attempted[-1]

		# Add emoji when successful
		await client.reaction_add(msg, BUILTIN_EMOJIS['fireworks'])
	except TimeoutError:
		await client.message_create(message.channel, "Guess I'll never know what the number was...")
	finally:
		guessing.remove(message.id)


telling: Set[int] = set()


async def guess_number(client: MapleClient, message: Message, lowest: int = 1, highest: int = 10):
	# Only allow one client to tell per command
	if message.id in telling:
		return
	telling.add(message.id)

	# Generate message and output prompt
	number = random.randint(lowest, highest)
	await client.message_create(
		message.channel,
		str(lowest).join(START_TEMPLATE) + str(highest)
	)

	try:
		# ID -> Guess Count
		guesses: Dict[int, int] = {}
		while True:
			guess_msg = await utils.wait_for_message(
				client,
				message.channel,
				is_msg_numeric,
				GUESS_WAIT_TIMEOUT
			)
			# Add one to existing count or set to 1
			guesses[guess_msg.author.id] = guesses.get(guess_msg.author.id, 0) + 1

			# If guess was correct, exit, otherwise send too high/low message
			guess = int(guess_msg.content)
			if guess == number:
				break

			await client.message_create(
				message.channel,
				INCORRECT_TEMPLATE.format(TOO_HIGH_KEYWORD if guess > number else TOO_LOW_KEYWORD)
			)

		# When guess is correct, output correct template with winner and guess count
		await client.message_create(
			message.channel,
			CORRECT_TEMPLATE.format(
				guess_msg.author,
				guesses[guess_msg.author.id]
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

def teardown(_: ModuleType):
	for client in CLIENTS:
		client.events.remove(message_create)
		client.commands.remove(guess_number)
