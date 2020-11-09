import time
import os


from hata.discord import KOKORO, CLIENTS, start_clients, stop_clients
from hata.ext.extension_loader import EXTENSION_LOADER


from config import create_clients, MapleClient


async def ready(client: MapleClient):
	# TODO - output info for client
	print(f'{client:f} logged in.')

if __name__ == '__main__':
	create_clients()
	for client in CLIENTS:
		client.events(ready)

	for extension_name in [filename for filename in os.listdir('extensions') if filename.endswith('.py')]:
		EXTENSION_LOADER.add('extensions.' + extension_name[:-3])
	EXTENSION_LOADER.load_all()

	print('Connecting...')
	start_clients()
	try:
		time.sleep(2000.5)
	except KeyboardInterrupt:
		stop_clients()
		print('Disconnected')
		KOKORO.stop()
