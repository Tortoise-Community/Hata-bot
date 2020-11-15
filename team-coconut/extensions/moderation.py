from hata import eventlist, Message, Client, CLIENTS
from hata.ext.commands import Command

MODERATION_COMMANDS = eventlist(type_=Command)
Bcom: Client

def setup(lib):
    category = Bcom.command_processer.get_category("moderation")
    if not category:
        Bcom.command_processer.get_category("moderation")
    Bcom.commands.extend(MODERATION_COMMANDS)

def teardown(lib):
    Bcom.commands.unextend(MODERATION_COMMANDS)

@MODERATION_COMMANDS.from_class
class test:
    category = 'moderation'

    async def command(client: Client, message: Message):
        await client.message_create(message.channel, 'Main Client' + client.mention)
        for client in CLIENTS:
            await client.message_create(message.channel, 'hi')
