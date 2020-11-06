from config import WHITELISTED_OWNERS
from hata import CLIENTS, Client, Message
from hata.ext.commands.command import checks


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


ALL = wrapper()
