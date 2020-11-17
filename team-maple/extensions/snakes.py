from hata.backend.futures import sleep
from hata.discord.channel import ChannelText
from hata.discord.user import UserBase
import random
from utils import is_exclusive_command
from PIL import Image, ImageDraw
from typing import List, Set, cast, Tuple, Union, Dict
from types import ModuleType


from hata.discord import Message, Color, Embed, CLIENTS
from hata.backend import ReuBytesIO


from config import MapleClient, CLIENT_INFO
"""
	try:
		with ReuBytesIO() as buffer:
			if len(message.content) == 8 and message.content.lower().startswith('0x'):
				img = Image.new('RGB', (150, 150), color=Color(int(message.content, base=16)).as_tuple)
				img.save(buffer, 'png')
				buffer.seek(0)
				await client.message_create(message.channel, file=('color.png', buffer))
			img = Image.new('RGB', (150, 150), color=message.content)
			img.save(buffer, 'png')
			buffer.seek(0)
			await client.message_create(message.channel, file=('color.png', buffer))
	except:
		return
"""

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
	#v_padding = BOARD_TILE_PADDING-1 if v % 2 == 0 else BOARD_TILE_PADDING
	for h in range(BOARD_HORIZONTAL_TILES):
		#h_padding = BOARD_TILE_PADDING-1 if h % 2 == 0 else BOARD_TILE_PADDING
		x = BOARD_ONE_TOPLEFT[0] + (BOARD_TILE_SIZE * h) + (BOARD_TILE_PADDING * h)
		y = BOARD_ONE_TOPLEFT[1] - (BOARD_TILE_SIZE * v) - (BOARD_TILE_PADDING * v)
		num += 1
		BOARD_MAP[num] = (x, y, [])

for s, e in (
	(11, 20),
	(31, 40),
	(51, 60),
	(71, 80),
	(91, 100),
):
	for i in range(s, e+1):
		j = s + e - i
		if i > j:
			continue
		temp = BOARD_MAP[i]
		BOARD_MAP[i] = BOARD_MAP[j]
		BOARD_MAP[j] = temp

dump_channel = ChannelText.precreate(774699107456778250)

COLORS = ['red', 'green', 'blue', 'purple', 'yellow', 'aqua']

def generate_frame(player_positions: Dict[int, List[Tuple[UserBase, Tuple[int, int, int]]]], base: Image):
	frame = base.copy()
	draw = ImageDraw.Draw(frame)
	for cell, players in player_positions.items():
		tile = BOARD_MAP[cell]
		xy = (tile[0], tile[1], tile[0] + BOARD_TILE_SIZE, tile[1] + BOARD_TILE_SIZE)
		player_count = len(players)
		for i, (user, color) in enumerate(players):
			draw.arc(xy, (i/player_count)*360, ((i+1)/player_count)*360, color, 10)
#			for cell, tile in BOARD_MAP.items():
#				draw.rectangle((tile[0], tile[1], tile[0] + BOARD_TILE_SIZE, tile[1] + BOARD_TILE_SIZE), fill=None, outline=(255, 0, 0), width=3)
#				draw.text((tile[0], tile[1]), str(cell), fill=(0, 0, 0))
	return frame

def generate_frames(player_positions: Dict[int, List[Tuple[UserBase, Tuple[int, int, int]]]]):
	frames = []
	won = False
	base = Image.open('board.png')
	base = base.convert('RGB')
	while not won:
		frames.append(generate_frame(player_positions, base))
		for cell, players in list(player_positions.items())[:]:
			for player in players[:]:
				old_cell = cell
				if cell in SNAKES:
					cell = SNAKES[cell]
				elif cell in LADDERS:
					cell = LADDERS[cell]
				else:
					cell += random.randint(1, 6)

				if cell > 100:
					cell = 100

				if cell not in player_positions:
					player_positions[cell] = []
				player_positions[cell].append(player)
				if player in player_positions[old_cell]:
					player_positions[old_cell].remove(player)

				if cell == 100:
					won = player[0]
					break

				cell = old_cell

			if won:
				break

	frames.append(generate_frame(player_positions, base))

	return frames, won

async def snakes(client: MapleClient, message: Message):
	"""Start a game of snakes-and-ladders"""
	embed = Embed('Snakes & Ladders', 'Game time!')
	embed.add_image('attachment://board.gif')
	available_colors = COLORS[:]
	#players: Dict[UserBase, List[Union[int, Tuple[int, int, int]]]] = {
#		client: [1, available_colors.pop()],
#		message.author: [1, available_colors.pop()]
#	}
	player_positions: Dict[int, List[Tuple[UserBase, Tuple[int, int, int]]]] = {
		1: [
			(client, available_colors.pop()),
			(message.author, available_colors.pop()),
		]
	}
	# TODO - prompt who wants to play snakes and ladders
	for other_client in CLIENTS:
		if other_client is client:
			continue
		player_positions[1].append((other_client, available_colors.pop()))


	await client.typing(message.channel)
	frames, won = generate_frames(player_positions)
	with ReuBytesIO() as buffer:
		frames[0].save(buffer, save_all=True, format='gif', append_images=frames[1:], duration=1000, optimize=False, loop=0)
		buffer.seek(0)

		atch_msg = await client.message_create(dump_channel, 'text to make deletable...?', file=('board.gif', buffer))
		url = atch_msg.attachments[0].url

		game_msg = await client.message_create(message.channel, url)

	#await client.message_create(message.channel, '{:m} won!'.format(won))


def setup(_: ModuleType):
	for client in CLIENTS:
		client.commands(checks=[is_exclusive_command()])(snakes)


def teardown(_: ModuleType):
	for client in CLIENTS:
		client.commands.remove(snakes)
