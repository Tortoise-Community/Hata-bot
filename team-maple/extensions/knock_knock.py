import random
from typing import Dict, Tuple
from types import ModuleType


from hata.discord import Message, CLIENTS, BUILTIN_EMOJIS


from config import MapleClient


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

telling: Dict[int, Tuple[int, int]] = {}
receiving: Dict[int, Tuple[int, int]] = {}

started_responding = False


async def message_create(client: MapleClient, message: Message):
	global started_responding
	if client.id != message.author.id and 'knock knock' in message.content.lower() and not started_responding:
		started_responding = True
		await client.message_create(message.channel, "Who's there?")
		receiving[client.id] = [message.author.id, 0]
		started_responding = False
		return

	if client.id in receiving:
		partner, stage = receiving[client.id]
		if partner != message.author.id:
			return
		if stage == 0:
			await client.message_create(message.channel, '{} who?'.format(message.content))
			receiving[client.id][1] += 1
		elif stage == 1:
			await client.reaction_add(message, BUILTIN_EMOJIS['laughing'])
			del receiving[client.id]
	elif client.id in telling:
		index, stage = telling[client.id]
		if stage == 0 and message.content.lower() == "who's there?":
			await client.message_create(message.channel, KNOCK_KNOCK_JOKES[index][0])
			telling[client.id][1] += 1
		elif stage == 1 and message.content.lower() == '{} who?'.format(KNOCK_KNOCK_JOKES[index][0].lower()):
			await client.message_create(message.channel, KNOCK_KNOCK_JOKES[index][1])
			del telling[client.id]


exclusive_knock_knock = False


async def knock_knock(client: MapleClient, message: Message):
	"""Tell a knock knock joke"""
	global exclusive_knock_knock
	if exclusive_knock_knock:
		return
	exclusive_knock_knock = True

	index = random.randrange(len(KNOCK_KNOCK_JOKES))
	telling[client.id] = [index, 0]
	await client.message_create(message.channel, 'Knock Knock')

	exclusive_knock_knock = False


def setup(_: ModuleType):
	for client in CLIENTS:
		client.events(message_create)
		client.commands(knock_knock)
