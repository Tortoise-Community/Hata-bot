import asyncio
from time import time
from hata import backend, discord
from hata.ext import commands
from hata.discord import client_core
from . import constants

# IDEA: voice chat grabber??? 

class ChatGrabber:
    def __init__(
        self, 
        client, 
        origin, 
        destination=None, 
        users=None, 
        only_users=False, 
        timeout=None, 
        fmt=None,
        start_hook=None,
        stop_hook=None,
        destination_to_origin=False
    ):
        self.client = client
        self.timeout = timeout
        self.origin = origin
        self.destination = destination
        self.cancellation_votes = []
        self.users = users or {}
        self.only_users = only_users
        self.fmt = fmt or '**{0.author.name}#{0.author.discriminator}**: {0.content}'
        self.started = False
        self.stopped = False
        self.start_hook = start_hook
        self.stop_hook = stop_hook
        self.destination_to_origin = destination_to_origin
        self.destination_future = backend.Future(client_core.KOKORO)
        self._current_future = None

    def set_destination(self, destination) -> None:
        self.destination = destination
        try:
            self.destination_future.set_result(destination)
        except backend.InvalidStateError:
            pass

    def add_user(self, user) -> None:
        self.users[user.id] = {'user': user, 'time': time()}

    def remove_user(self, user) -> None:
        del self.users[user.id]

    def check(self, message) -> bool:
        if message.author.id == self.client.id:
            return False
        if message.channel not in (self.origin, self.destination):
            return False
        if self.only_users:
            if message.author not in self.users:
                return False
        if message.author.id in self.users or not self.only_users:
            self.add_user(message.author)
        return True

    async def origin_send(self, client, message) -> None:
        if not self.check(message):
            return
        self._current_future.set_result(message)
        self._current_future = backend.Future(client_core.KOKORO)
        await self.client.message_create(self.origin, self.fmt.format(message))

    async def destination_send(self, client, message) -> None:
        if not self.check(message):
            return
        self._current_future.set_result(message)
        self._current_future = backend.Future(client_core.KOKORO)
        await self.client.message_create(self.destination, self.fmt.format(message))

    async def start(self) -> None:
        self.started = True
        self._current_future = backend.Future(client_core.KOKORO)
        self.client.command_processer.append(self.origin, self.destination_send)
        if self.destination_to_origin:
            self.client.command_processer.append(self.destination, self.origin_send)
        if self.start_hook is not None:
            await self.start_hook(self)
        while True:
            if self.timeout is not None:
                backend.future_or_timeout(self._current_future, self.timeout)
            try:
                await self._current_future
            except (TimeoutError, backend.CancelledError):
                if not self.stopped:
                    await self.stop()
                return

    async def stop(self) -> None:
        self.stopped = True
        self.client.command_processer.remove(self.origin, self.destination_send)
        if self.destination_to_origin:
            self.client.command_processer.remove(self.destination, self.origin_send)
        if self.stop_hook is not None:
            await self.stop_hook(self)
        if self._current_future is not None:
            try:
                self._current_future.cancel()
            except backend.InvalidStateError:
                pass

def procude_infraction_embed(*, case_number, what_happened, case_type, reason, moderator, until=None):
    description = [
        what_happened,
        '**Type:** {}'.format(case_type.capitalize()),
        '**Reason:** {}'.format(reason),
        '**Moderator:** {0.full_name} (ID: {0.id})'.format(moderator)
    ]
    if until is not None:
        description.append(
            '**Until:** {}'.format(until)
        )
    embed = discord.Embed(
        color=constants.Colors.RED, 
        title='Case #{}'.format(case_number),
        description='\n'.join(description)
    )
    return embed

def hata_fut_from_asyncio_task(client, coro):
    loop = client._asyncio_event_loop
    task = asyncio.run_coroutine_threadsafe(coro, loop=loop)
    fut = backend.Future(client_core.KOKORO)
    def set_result(future):
        client_core.KOKORO.call_soon_threadsafe(fut.set_result, future.result())
    task.add_done_callback(set_result)
    return fut

async def try_send(client, *args, **kwargs):
    try:
        message = await client.message_create(*args, **kwargs)
    except discord.DiscordException:
        return None
    else:
        return message

async def try_create_dm(client, user):
    try:
        dm = await client.channel_private_create(user)
    except discord.DiscordException:
        return None
    else:
        return dm