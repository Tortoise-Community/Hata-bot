import config
from hata import Client
from hata.ext.commands import setup_ext_commands
from hata.ext.commands.helps.subterranean import SubterraneanHelpCommand

Bcom: Client
setup_ext_commands(Bcom, config.BCOM_PREFIX)
Bcom.commands(SubterraneanHelpCommand(), 'help')
