from hata import eventlist, Message, Client, CLIENTS
from hata.ext.commands import Command

MODERATION_COMMANDS = eventlist(type_=Command)
Reimu: Client


def setup(lib):
    category = Reimu.command_processer.get_category('MODERATION')
    if not category:
        Reimu.command_processer.create_category('MODERATION', )

    Reimu.commands.extend(MODERATION_COMMANDS)


def teardown(lib):
    Reimu.commands.unextend(MODERATION_COMMANDS)


# @MODERATION_COMMANDS.from_class
# class test:
#     category = 'ADMINISTRATION'
#
#     async def command(client: Client, message: Message):
#         await client.message_create(message.channel, 'Main Client' + client.mention)
#         for client in CLIENTS:
#             await client.message_create(message.channel, 'hi')
