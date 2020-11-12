import random
import re
from typing import Optional, Set, List
from types import ModuleType


from hata.discord import Message, Embed, CLIENTS, BUILTIN_EMOJIS
from hata.discord.parsers import ReactionAddEvent
from hata.ext.commands import utils


from config import MapleClient


WORDBANK = [
	'Hello, World!',
	'Hata',
	'Tortoise',
	'Maple',
	'Discord'
]

START_HANGMAN_MESSAGE = 'Who wants to play hangman?'
START_HANGMAN_EMOJI_NAME = 'raised_hand'

GUESS_WAIT_TIMEOUT = 30


def generate_hangman_embed(word: List[str], current: List[str], lives: int, won: Optional[bool], msg: str = ''):
	full_msg = '\n' + msg if msg else ''
	msg_and_word = '{}```\n{{}}\n```'.format(full_msg)
	embed = Embed('Hangman')
	if won is None:
		embed.description = '{} lives remaining...{}'.format(lives, msg_and_word.format(''.join(current)))
	elif won:
		embed.description = 'You won with {} lives remaining!{}'.format(lives, msg_and_word.format(''.join(current)))
	else:
		embed.description = 'You lost...{}'.format(msg_and_word.format(''.join(word)))
	return embed


active_games: Set[int] = set()


async def hangman(client: MapleClient, message: Message, guessing_word: str = ''):
	"""Start a game of hangman"""
	global active_games
	if message.id in active_games:
		return
	active_games.add(message.id)

	random_word = guessing_word or random.choice(WORDBANK)
	word = list(random_word)
	current: List[str] = list(re.sub('[a-zA-Z]', '_', random_word))
	lives = 6
	won: Optional[bool] = None

	await client.typing(message.channel)
	hangman_msg = await client.message_create(message.channel, START_HANGMAN_MESSAGE)
	await client.reaction_add(hangman_msg, BUILTIN_EMOJIS[START_HANGMAN_EMOJI_NAME])
	try:
		event: ReactionAddEvent = await utils.wait_for_reaction(
			client,
			hangman_msg,
			lambda event: event.user.id != client.id and event.emoji.name == START_HANGMAN_EMOJI_NAME,
			GUESS_WAIT_TIMEOUT
		)
	except TimeoutError:
		await client.message_edit(hangman_msg, 'Guess nobody wants to play hangman...')
		return
	finally:
		await client.reaction_delete_emoji(hangman_msg, BUILTIN_EMOJIS[START_HANGMAN_EMOJI_NAME])

	other_id = event.user.id

	await client.message_edit(hangman_msg, '', embed=generate_hangman_embed(word, current, lives, won))

	try:
		while won is None:
			guess_msg = await utils.wait_for_message(
				client,
				message.channel,
				lambda msg: msg.author.id == other_id and len(msg.content) == 1 and msg.content[0].isalpha(),
				GUESS_WAIT_TIMEOUT
			)
			await client.typing(message.channel)
			letter: str = guess_msg.content[0].lower()
			await client.message_delete(guess_msg)

			response = ''
			if letter in current or letter.upper() in current:
				response = "You have already guessed `{}` ".format(letter)
			else:
				found = False
				for i, correct in enumerate(word):
					if correct.lower() == letter:
						current[i] = correct
						found = True
				if not found:
					lives -= 1

				if word == current:
					won = True
				elif lives == 0:
					won = False

			await client.message_edit(hangman_msg, embed=generate_hangman_embed(word, current, lives, won, response))
	except TimeoutError:
		won = False
		await client.message_edit(
			hangman_msg,
			embed=generate_hangman_embed(word, current, lives, won, 'The game was abandoned')
		)

	active_games.remove(message.id)


def setup(_: ModuleType):
	for client in CLIENTS:
		client.commands(hangman)
