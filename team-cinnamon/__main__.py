import logging
import asyncio
from hata.ext.commands import setup_ext_commands
from importlib import import_module
from bot.client import Client
from bot.logger import Logger
from website.server import Server
from bot import constants
from database.database import Database

client = Client(constants.Auth.BOT_TOKEN)
setup_ext_commands(client, client._get_prefix)
client.server = Server(client=client)
client.database = Database(client=client)
client.logger = Logger(client=client)

logging.basicConfig(level=logging.DEBUG)

client.load_extension(import_module('.extensions.main', package='bot').Main())
client.load_extension(import_module('.extensions.fun', package='bot').Fun())
client.load_extension(import_module('.extensions.moderation', package='bot').Moderation())

client.login()
