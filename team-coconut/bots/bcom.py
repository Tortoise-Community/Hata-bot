from hata import Client, Message
from hata.ext.commands import setup_ext_commands
from hata.ext.commands.helps.subterranean import SubterraneanHelpCommand

import config

Bcom: Client
setup_ext_commands(Bcom, config.BCOM_PREFIX)
Bcom.commands(SubterraneanHelpCommand(), 'help')


@Bcom.commands
async def tell(client: Client, message: Message, *text: str):
    await client.message_create(message.channel, ','.join(text))
