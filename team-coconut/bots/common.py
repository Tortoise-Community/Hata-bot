import inspect
from itertools import cycle

from config import CORE_GUILD
from hata import Client, Message, CLIENTS, User
from utils.utils import ALL, owneronly, SEQUENTIAL_ASK_NEXT

clients = cycle(CLIENTS)


@ALL.events
async def message_create(client: Client, message: Message):
    if message.author is client:
        return
    if message.author in CLIENTS:
        if message.content.strip().casefold().startswith(client.command_processer.prefix):
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


@ALL.commands(checks=owneronly)
async def source(client: Client, message: Message, command: str):
    if command == 'source':
        return
    if command not in client.command_processer.commands.keys():
        return await client.message_create(message.channel, f'Command {command} not found')
    code = inspect.getsource(client.command_processer.commands[command].command)
    await client.message_create(message.channel, '```py\n' + code + '\n```')

@Reimu.commands
class lookup(SEQUENTIAL_ASK_NEXT):
    async def __call__(self, client: Client, message: Message, user: User):
        await self._exec(client, message, user)

    async def before_exec(self, client, message, user):
        self.message_sent = await client.message_create(message.channel, f'Searching for {user.name}')

    async def function(self, client, message, user):
        method = client.message_edit
        channel = self.message_sent
        if user.is_bot:
            method = client.message_create
            channel = message.channel
        await method(channel, content=f'{user.mention} is in {len(user.guild_profiles)} servers as we are')

    async def singlefunction(self, client, message, user):
        method = client.message_edit
        channel = self.message_sent
        if user.is_bot:
            method = client.message_create
            channel = message.channel
        count = len([x for x in user.guild_profiles if client.id in x.users])
        await method(channel, content=f'{user.name} is in {count} servers as I am')
