# from config import WHITELISTED_OWNERS
# from hata import CLIENTS, Client, Message
from hata import CLIENTS


class wrapper:
    def commands(self, func=None, **kwargs):
        if func is None:
            return self.wrap(**kwargs)
        return self.wrap(**kwargs)(func)

    def wrap(self, **kwargs):
        def addfunc(func):
            for client in CLIENTS:
                client.commands(**kwargs)(func)
            return func

        return addfunc

    def events(self, func, *args, **kwargs):
        for client in CLIENTS:
            client.events(*args, **kwargs)(func)
        return func


# async def owneronly(client: Client, message: Message, *args, **kwargs):
#     if message.author.id not in WHITELISTED_OWNERS:
#         await client.message_create(message.channel, 'You dont have perms to use this command')
#         return False
#     return True

def colourfunc(client, message, name):
    return message.author.color_at(message.guild)


ALL = wrapper()
