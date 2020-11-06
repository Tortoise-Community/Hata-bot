import inspect
from config import WHITELISTED_OWNERS
from hata import Client, Message, CLIENTS
from utils.utils import ALL

Reimu: Client
Bcom: Client


@ALL.events
async def message_create(client: Client, message: Message):
    if message.author is client:
        return
    if message.author in CLIENTS:
        if message.content.strip().casefold().startswith(client.command_processer.prefix):
            print(client.name, message.content)
            message.author.is_bot = False
            await client.command_processer(client, message)
            message.author.is_bot = True
    if message.author.is_bot:
        return

@ALL.events
async def ready(client):
    print(f'{client:f} logged in.')


@ALL.commands
async def ping(client: Client, message: Message):
    await client.message_create(message.channel, f'{client.gateway.latency * 1000.:.0f} ms')


@ALL.commands
async def source(client: Client, message: Message, command: str):
    if message.author.id not in WHITELISTED_OWNERS:
        return await client.message_create(message.channel, 'You dont have perms to use this command')
    if command == 'source':
        return
    if command not in client.command_processer.commands.keys():
        return await client.message_create(message.channel, f'Command{command}not found')
    code = inspect.getsource(client.command_processer.commands[command].command)
    await client.message_create(message.channel, '```py\n' + code + '\n```')
