from audioop import add as add_voice

from config import CORE_GUILD
from config import WHITELISTED_OWNERS
from hata import CLIENTS, Client, Message, Webhook
from hata.discord.opus import OpusDecoder
from hata.discord.player import AudioSource
from hata.ext.commands.command import checks


def getseq():
    client_sequence = {}
    for pos, _client in enumerate(CLIENTS):
        if len(CLIENTS) == pos + 1:
            client_sequence[_client.id] = list(CLIENTS)[-1]
        else:
            client_sequence[_client.id] = list(CLIENTS)[pos + 1]
    return client_sequence


class wrapper:
    def commands(self, func=None, **kwargs):
        if func is None:
            return self.wrap('w', **kwargs)
        return self.wrap('w', **kwargs)(func)

    def wrap(self, m, **kwargs):
        def addfunc(func):
            for client in CLIENTS:
                if m == 'w':
                    client.commands(**kwargs)(func)
                elif m == 'e':
                    client.events(**kwargs)(func)
            return func

        return addfunc

    def events(self, func=None, **kwargs):
        if func is None:
            return self.wrap('e', **kwargs)
        return self.wrap('e', **kwargs)(func)


async def owneronly(client: Client, message: Message, *args, **kwargs):
    if message.author.id not in WHITELISTED_OWNERS:
        return False
    return True


owneronly = [checks.custom(function=owneronly)]


def colourfunc(client, message, name):
    return message.author.color_at(message.guild)


async def send(client: Client, webhook: Webhook, message: Message):
    await client.webhook_send(webhook, message.content, avatar_url=message.author.avatar_url, name=message.author.name)


class SEQUENTIAL_ASK_NEXT:
    async def _exec(self, client: Client, message: Message, *args):
        await self.before_exec(client, message, *args)
        _next = getseq()[client.id]
        if message.author not in CLIENTS:
            if message.guild.id != CORE_GUILD:
                return await self.function(client, message, *args)
            res = await self.singlefunction(client, message, *args)
            if res:
                await client.message_create(message.channel, f'Asking {_next.mention}')
                await client.message_create(message.channel, f'{_next.command_processer.prefix}lookup {"".join(args)}')
        else:
            if message.guild.id == CORE_GUILD:
                res = await self.singlefunction(client, message, *args)
                if res:
                    await client.message_create(message.channel, f'Asking {_next.mention}')
                    return await client.message_create(message.channel,
                                                       f'{_next.command_processer.prefix}lookup {"".join(args)}')
                return await self.function(client, message, *args)


class MixerStream(AudioSource):
    __slots__ = ('_decoder', '_postprocess_called', 'sources',)

    def __init__(self, *sources):
        self.sources = list(sources)
        self._decoder = OpusDecoder()
        self._postprocess_called = False

    async def postprocess(self):
        if self._postprocess_called:
            return

        self._postprocess_called = True
        for source in self.sources:
            await source.postprocess()

    async def add(self, source):
        if self._postprocess_called:
            await source.postprocess()

        self.sources.append(source)

    async def read(self):
        sources = self.sources
        result = None

        for index in reversed(range(len(sources))):
            source = sources[index]
            data = await source.read()
            if data is None:
                del sources[index]
                await source.cleanup()
                continue
            if not source.NEEDS_ENCODE:
                data = self._decoder.decode(data)
            if result is None:
                result = data
            else:
                result = add_voice(result, data, 1)
            continue
        return result

    async def cleanup(self):
        self._postprocess_called = False
        sources = self.sources
        while sources:
            source = sources.pop()
            await source.cleanup()


def setdefault(_dict, val, default):
    _dict[val] = _dict.get(val, default)


ALL = wrapper()
