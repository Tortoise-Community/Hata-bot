from hata import Client, Message
from hata.ext.commands import setup_ext_commands
from hata.ext.commands.helps.subterranean import SubterraneanHelpCommand

import config

Reimu: Client
setup_ext_commands(Reimu, config.REIMU_PREFIX)
Reimu.commands(SubterraneanHelpCommand(), 'help')


@Reimu.commands
async def tell(client: Client, message: Message, *text: str):
    await client.message_create(message.channel, ','.join(text))
