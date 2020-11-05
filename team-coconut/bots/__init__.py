import os

from hata import Client, CLIENTS
from hata.ext.extension_loader import EXTENSION_LOADER

import config

Reimu = Client(config.REIMU_TOKEN)
Reimu.name = 'Reimu'

Bcom = Client(config.BCOM_TOKEN)
Bcom.name = 'Bcom'

Crambor = Client(config.CRAMBOR_TOKEN)
Crambor.name = 'Crambor'

CLIENT_CONTEXT = {}

for client in CLIENTS:
    CLIENT_CONTEXT[client.name] = client

for client in CLIENTS:
    EXTENSION_LOADER.load_extension('bots.' + client.name.lower(), **CLIENT_CONTEXT)

EXTENSIONS = []

for path in os.listdir('extensions'):
    if path.endswith('.py'):
        EXTENSIONS.append(path[:-3])

for path in EXTENSIONS:
    EXTENSION_LOADER.add('extensions.'+path, **CLIENT_CONTEXT)

EXTENSION_LOADER.load_all()
