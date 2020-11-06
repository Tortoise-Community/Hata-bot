import config

from hata import Client
from hata.ext.commands import setup_ext_commands
from hata.ext.commands.helps.subterranean import SubterraneanHelpCommand


Astra: Client
setup_ext_commands(Astra, config.ASTRA_PREFIX)
Astra.commands(SubterraneanHelpCommand(), 'help')
