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


@ALL.commands
async def ping(client: Client, message: Message):
    await client.message_create(message.channel, f'{client.gateway.latency*1000.:.0f} ms')
