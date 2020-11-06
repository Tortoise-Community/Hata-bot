from hata import Client
from hata.ext.commands import setup_ext_commands
from hata.ext.commands.helps.subterranean import SubterraneanHelpCommand

import config

Crambor: Client
setup_ext_commands(Crambor, config.CRAMBOR_PREFIX)
Crambor.commands(SubterraneanHelpCommand(), 'help')
