import random
from typing import Set
from types import ModuleType


from hata.discord import Message, CLIENTS, BUILTIN_EMOJIS
from hata.ext.commands import utils


from config import MapleClient


JOKE_RESPONSE_TIMEOUT = 15

KNOCK_KNOCK_JOKES = [
	["Ashe", "Bless you!"],
	["Nobel", "No bell, that's why I knocked!"],
	["Leaf", "Leaf me alone!"],
	["lettuce", "Lettuce in and you'll find out!"],
	["Aaron", "Why Aaron you opening the door?"],
	["Tank", "You're welcome!"],
	["Hawaii", "I'm fine, Hawaii you?"],
	["Orange", "Orange you even going to open the door!"],
	["Gray Z", "Gray Z mixed up kid."],
	["Who", "Is there an owl in there?"],
	["Anita", "Anita to borrow a pencil."],
	["Woo", "Don't get so excited, it's just a joke."],
	["Figs", "Figs the doorbell, it's broken!"],
	["Alice", "Alice fair in love and war."],
	["Annie", "Annie thing you can do, I can do better."],
	["Yukon", "Yukon say that again!"],
	["Boo", "Well you don't have to cry about it."],
	["Theodore", "Theodore is stuck and it won't open!"],
	["Cher", "Cher would be nice if you opened the door!"],
	["Amos", "A mosquito bit me!"],
	["Police", "Police let us in, it's cold out here!"],
	["Amarillo", "Amarillo nice guy."]
]


joke_tellers: Set[int] = set()
jokes_responded_to: Set[int] = set()


async def message_create(client: MapleClient, message: Message):
	if message.id in jokes_responded_to or client.id == message.author.id or 'knock knock' not in message.content.lower():
		return

	jokes_responded_to.add(message.id)

	await client.message_create(message.channel, "Who's there?")

	try:
		# Wait for first part of joke from original joke teller
		msg = await utils.wait_for_message(
			client,
			message.channel,
			lambda msg: msg.author.id == message.author.id,
			JOKE_RESPONSE_TIMEOUT
		)

		await client.message_create(message.channel, '{} who?'.format(msg.content))
		# Wait for punchline of joke from original joke teller
		msg = await utils.wait_for_message(
			client,
			message.channel,
			lambda msg: msg.author.id == message.author.id,
			JOKE_RESPONSE_TIMEOUT
		)

		await client.reaction_add(msg, BUILTIN_EMOJIS['laughing'])
	except TimeoutError:
		await client.message_create(message.channel, "Guess I'll never heard the end of that joke...")
	finally:
		jokes_responded_to.remove(message.id)


async def knock_knock(client: MapleClient, message: Message):
	"""Tell a knock knock joke"""
	if message.id in joke_tellers:
		return
	joke_tellers.add(message.id)

	joke_setup, joke_punchline = random.choice(KNOCK_KNOCK_JOKES)
	await client.message_create(message.channel, 'Knock Knock')

	try:
		# Wait for anybody to say "Who's there?"
		await utils.wait_for_message(
			client,
			message.channel,
			lambda msg: msg.content.lower() == "who's there?",
			JOKE_RESPONSE_TIMEOUT
		)

		await client.message_create(message.channel, joke_setup)

		# Wait for "X who?" question
		await utils.wait_for_message(
			client,
			message.channel,
			lambda msg: msg.content.lower() == "{} who?".format(joke_setup).lower(),
			JOKE_RESPONSE_TIMEOUT
		)

		await client.message_create(message.channel, joke_punchline)
	except TimeoutError:
		await client.message_create(message.channel, 'Guess nobody wanted to hear the joke...')
	finally:
		joke_tellers.remove(message.id)


def setup(_: ModuleType):
	for client in CLIENTS:
		client.events(message_create)
		client.commands(knock_knock)
