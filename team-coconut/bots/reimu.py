import config
from hata import Client
from hata.ext.commands import setup_ext_commands
from hata.ext.commands.helps.subterranean import SubterraneanHelpCommand
from utils.utils import colourfunc

Reimu: Client
setup_ext_commands(Reimu, config.REIMU_PREFIX)
Reimu.commands(SubterraneanHelpCommand(color=colourfunc), name='help')
