from hata import eventlist
from hata.ext.commands import Command, Client

MODERATION_COMMANDS = eventlist(type_=Command)
Reimu: Client


def setup(lib):
    category = Reimu.command_processer.get_category('MODERATION')
    if not category:
        Reimu.command_processer.create_category('MODERATION', )

    Reimu.commands.extend(MODERATION_COMMANDS)


def teardown(lib):
    Reimu.commands.unextend(MODERATION_COMMANDS)
