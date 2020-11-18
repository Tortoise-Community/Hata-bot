import os
import time
import random
from typing import List, Tuple, Dict, Set
from types import ModuleType


from PIL import Image, ImageDraw
from hata.discord import Message, Embed, CLIENTS, BUILTIN_EMOJIS, UserBase, DiscordException
from hata.backend import ReuBytesIO, sleep
from hata.ext.commands import utils


from config import MapleClient
from utils import is_exclusive_command

try:
	from pygifsicle import optimize
except:
	optimize = False


COLORS = ['red', 'brown', 'orange', 'purple', 'yellow', 'blue', 'green']
BOARD_FILEPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'snake_board.png')
BOARD_TILE_SIZE = 53
BOARD_TILE_PADDING = 2.5
BOARD_MAP = {}
BOARD_ONE_TOPLEFT = (29, 529)
BOARD_WIDTH = 10
BOARD_HORIZONTAL_TILES = 10
BOARD_VERTICAL_TILES = 10
SNAKES = {
	99: 41,
	89: 53,
	76: 58,
	66: 45,
	54: 31,
	43: 18,
	40: 3,
	27: 5,
}
LADDERS = {
	74: 92,
	62: 81,
	50: 69,
	42: 63,
	13: 46,
	4: 25
}
num = 0
for v in range(BOARD_VERTICAL_TILES):
	for h in range(BOARD_HORIZONTAL_TILES):
		x = BOARD_ONE_TOPLEFT[0] + (BOARD_TILE_SIZE * h) + (BOARD_TILE_PADDING * h)
		y = BOARD_ONE_TOPLEFT[1] - (BOARD_TILE_SIZE * v) - (BOARD_TILE_PADDING * v)
		num += 1
		BOARD_MAP[num] = (x, y, [])

for start, end in (
	(11, 20),
	(31, 40),
	(51, 60),
	(71, 80),
	(91, 100),
):
	for i in range(start, end + 1):
		j = start + end - i
		if i > j:
			continue
		temp = BOARD_MAP[i]
		BOARD_MAP[i] = BOARD_MAP[j]
		BOARD_MAP[j] = temp


def generate_frame(player_positions: Dict[int, List[Tuple[UserBase, Tuple[int, int, int]]]], base: Image.Image):
	frame: Image.Image = base.copy()
	draw: ImageDraw.ImageDraw = ImageDraw.Draw(frame)
	for cell, players in player_positions.items():
		tile = BOARD_MAP[cell]
		xy = (tile[0], tile[1], tile[0] + BOARD_TILE_SIZE, tile[1] + BOARD_TILE_SIZE)
		player_count = len(players)

		for i, (_, color) in enumerate(players):
			draw.arc(xy, (i / player_count) * 360, ((i + 1) / player_count) * 360, color, 10)

	return frame


def generate_frames(player_positions: Dict[int, List[Tuple[UserBase, Tuple[int, int, int]]]], all_frames: bool):
	base: Image.Image = Image.open(BOARD_FILEPATH).convert('RGB')

	frames = []
	turns = []
	won = None
	while won is None:
		frames.append(generate_frame(player_positions, base))
		turns.append(True)

		for cell, players in list(player_positions.items())[:]:
			for player in players[:]:
				old_cell = cell
				player_positions[old_cell].remove(player)

				if cell in SNAKES:
					cell = SNAKES[cell]
				elif cell in LADDERS:
					cell = LADDERS[cell]
				else:
					roll = random.randint(1, 6)
					if all_frames:
						for i in range(1, roll):
							cell = old_cell + i
							if cell > 100:
								break
							if cell not in player_positions:
								player_positions[cell] = []
							player_positions[cell].append(player)
							frames.append(generate_frame(player_positions, base))
							turns.append(False)
							player_positions[cell].remove(player)
					else:
						cell += roll

				if cell > 100:
					cell = 100

				if cell not in player_positions:
					player_positions[cell] = []
				player_positions[cell].append(player)

				if cell == 100:
					won = player[0]
					break

				cell = old_cell

			if won:
				break

	frames.append(generate_frame(player_positions, base))
	turns.append(True)

	return frames, turns, won


async def message_create(client: MapleClient, message: Message):
	await sleep(2)
	if (
		message.id in human_games
		or not message.content.startswith('Who wants to play Snakes and Ladders')
	):
		return

	await client.reaction_add(message, BUILTIN_EMOJIS['raised_hand'])


def generate_player_positions(prompt: Message):
	available_colors = COLORS[:]
	player_positions: Dict[int, List[Tuple[UserBase, Tuple[int, int, int]]]] = {
		1: []
	}
	for player in prompt.reactions[BUILTIN_EMOJIS['raised_hand']]:
		player_positions[1].append((player, available_colors.pop()))

	return player_positions

human_games: Set[int] = set()

async def snakes(client: MapleClient, message: Message, human_only: int = 0):
	"""Start a game of snakes-and-ladders"""
	prompt = await client.message_create(
		message.channel,
		'Who wants to play Snakes and Ladders?\n\nGame will start in {} seconds...'
		.format(60)
	)
	pid = prompt.id
	if human_only:
		human_games.add(pid)

	await client.reaction_add(prompt, BUILTIN_EMOJIS['raised_hand'])
	await client.reaction_add(prompt, BUILTIN_EMOJIS['checkered_flag'])
	try:
		await utils.wait_for_reaction(
			client,
			prompt,
			lambda event: event.user.id == message.author.id and event.emoji.name == 'checkered_flag',
			60
		)
	except TimeoutError:
		pass

	backup_player_positions = generate_player_positions(prompt)
	player_positions = generate_player_positions(prompt)

	await client.message_delete(prompt)

	desc = '..and the FULL_DUR second game begins!\nPlaying are:\n\n'
	for player, color in player_positions[1]:
		desc += '{:e}: {:m}\n'.format(BUILTIN_EMOJIS[color + '_square'], player)

	with client.keep_typing(message.channel):
		for all_frames in range(2):
			if all_frames:
				print('Generating minimal amount of frames...')
				player_positions = backup_player_positions

			frames, turns, won = generate_frames(player_positions, not all_frames)
			durations = [(1000 if turns[f] else 250) if f != len(frames) - 1 else 10000 for f in range(len(frames))]
			duration = int(sum(durations) / 1000)

			embed = Embed('Snakes & Ladders', desc.replace('FULL_DUR', str(duration - 10)))
			embed.add_image('attachment://gameplay.gif')

			with ReuBytesIO() as buffer:
				frames[0].save(
					buffer,
					save_all=True,
					format='gif',
					append_images=frames[1:],
					duration=durations,
					optimize=True
				)
				buffer.seek(0)

				try:
					gameplay = await client.message_create(
						message.channel,
						embed=embed,
						file=('gameplay.gif', buffer)
					)
					break
				except DiscordException:
					print('Gameplay too large')
					if not optimize:
						print('pygifsicle not installed, cannot optimize')
						continue
					buffer.truncate(0)
					filename = '{}.gif'.format(time.time())
					frames[0].save(
						filename,
						save_all=True,
						format='gif',
						append_images=frames[1:],
						duration=durations,
						optimize=True
					)
					try:
						optimize(filename)
						with open(filename, 'rb') as image_file:
							buffer.write(image_file.read())
							buffer.seek(0)
						gameplay = await client.message_create(
							message.channel,
							embed=embed,
							file=('gameplay.gif', buffer)
						)
						os.unlink(filename)
						break
					except FileNotFoundError:
						print('gifsicle not installed, cannot optimize')
						pass
					except DiscordException:
						print('Gameplay still too large')

	await sleep(duration)
	embed.description = embed.description.replace(
		embed.description.split('\n')[0],
		'{:m} won after {} seconds!'.format(won, duration - 10)
	)
	await client.message_edit(gameplay, embed=embed)
	if human_only:
		human_games.remove(pid)


def setup(_: ModuleType):
	for client in CLIENTS:
		client.events(message_create)
		client.commands(checks=[is_exclusive_command()])(snakes)


def teardown(_: ModuleType):
	for client in CLIENTS:
		client.events.remove(message_create)
		client.commands.remove(snakes)
