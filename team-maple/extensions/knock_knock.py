import os
import random
from typing import List, Tuple, Set
from types import ModuleType


from hata.discord import Message, CLIENTS, BUILTIN_EMOJIS
from hata.backend import sleep
from hata.ext.commands import utils


from config import MapleClient
from utils import is_exclusive_command, make_exclusive_event


JOKE_RESPONSE_TIMEOUT = 15

KNOCK_KNOCK_JOKES: List[Tuple[str, str]] = [
	("Ashe", "Bless you!"),
	("Nobel", "No bell, that's why I knocked!"),
	("Leaf", "Leaf me alone!"),
	("lettuce", "Lettuce in and you'll find out!"),
	("Aaron", "Why Aaron you opening the door?"),
	("Tank", "You're welcome!"),
	("Hawaii", "I'm fine, Hawaii you?"),
	("Orange", "Orange you even going to open the door!"),
	("Gray Z", "Gray Z mixed up kid."),
	("Who", "Is there an owl in there?"),
	("Anita", "Anita to borrow a pencil."),
	("Woo", "Don't get so excited, it's just a joke."),
	("Figs", "Figs the doorbell, it's broken!"),
	("Alice", "Alice fair in love and war."),
	("Annie", "Annie thing you can do, I can do better."),
	("Yukon", "Yukon say that again!"),
	("Boo", "Well you don't have to cry about it."),
	("Theodore", "Theodore is stuck and it won't open!"),
	("Cher", "Cher would be nice if you opened the door!"),
	("Amos", "A mosquito bit me!"),
	("Police", "Police let us in, it's cold out here!"),
	("Amarillo", "Amarillo nice guy.")
]

try:
	with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'knock_knock_jokelist.txt'), 'r') as jokelist_file:
		KNOCK_KNOCK_JOKES = [tuple(joke.split('|')) for joke in jokelist_file.read().split('\n') if joke.strip()]
	print(f'{len(KNOCK_KNOCK_JOKES)} knock-knock jokes loaded from joke list')
except:
	pass

START_MESSAGE = 'Knock Knock'
WHO_MESSAGE = "Who's there?"
BLANK_WHO_TEMPLATE = '{} who?'


@make_exclusive_event
async def message_create(client: MapleClient, message: Message):
	# Sleep to provide enough time for human_games to get message ID added to it
	await sleep(1)

	# If joke already handled, is self, or not a knock knock prompt, return
	if (
		client.id == message.author.id
		or START_MESSAGE.lower() not in message.content.lower()
		or message.id in human_jokes
	):
		return

	# Ask who
	await client.human_delay(message.channel)
	await client.message_create(message.channel, WHO_MESSAGE)

	try:
		# Wait for first part of joke from original joke teller
		setup_msg = await utils.wait_for_message(
			client,
			message.channel,
			lambda setup_msg: setup_msg.author.id == message.author.id,
			JOKE_RESPONSE_TIMEOUT
		)

		await client.human_delay(message.channel)
		await client.message_create(message.channel, BLANK_WHO_TEMPLATE.format(setup_msg.content))

		# Wait for punchline of joke from original joke teller
		punch_msg = await utils.wait_for_message(
			client,
			message.channel,
			lambda punch_msg: punch_msg.author.id == message.author.id,
			JOKE_RESPONSE_TIMEOUT
		)

		await client.human_delay()
		await client.reaction_add(punch_msg, BUILTIN_EMOJIS['laughing'])
	except TimeoutError:
		await client.message_create(message.channel, "Guess I'll never hear the end of that joke...")


human_jokes: Set[int] = set()

async def knock_knock(client: MapleClient, message: Message, human_only: int = 0):
	"""Tell a knock knock joke"""
	joke_setup, joke_punchline = random.choice(KNOCK_KNOCK_JOKES)
	prompt = await client.message_create(message.channel, START_MESSAGE)
	if human_only:
		human_jokes.add(prompt.id)

	try:
		# Wait for anybody to say "Who's there?"
		await utils.wait_for_message(
			client,
			message.channel,
			lambda msg: msg.content.lower() == WHO_MESSAGE.lower(),
			JOKE_RESPONSE_TIMEOUT
		)

		# Send joke setup
		await client.message_create(message.channel, joke_setup)

		# Wait for "X who?" question
		await utils.wait_for_message(
			client,
			message.channel,
			lambda msg: msg.content.lower() == BLANK_WHO_TEMPLATE.format(joke_setup).lower(),
			JOKE_RESPONSE_TIMEOUT
		)

		# Send joke punchline
		await client.message_create(message.channel, joke_punchline)
	except TimeoutError:
		await client.message_create(message.channel, 'Guess nobody wanted to hear the joke...')
	finally:
		if human_only:
			human_jokes.remove(prompt.id)

def setup(_: ModuleType):
	for client in CLIENTS:
		client.events(message_create)
		client.commands(checks=[is_exclusive_command()])(knock_knock)


def teardown(_: ModuleType):
	for client in CLIENTS:
		client.events.remove(message_create)
		client.commands.remove(knock_knock)
