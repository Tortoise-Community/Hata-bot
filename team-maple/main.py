import time


from dotenv import load_dotenv
load_dotenv()
from hata.discord import KOKORO, start_clients, stop_clients, Client
from hata.ext.extension_loader import EXTENSION_LOADER


from config import CLIENT_INFO



async def ready(client: Client):
	# TODO - output info for client
	print(f'{client:f} logged in.')

if __name__ == '__main__':
	EXTENSION_LOADER.add_default_variables(CLIENT_INFO=CLIENT_INFO)
	for info in CLIENT_INFO.values():
		client = info['CLIENT']
		client.events(ready)

		for extension_name in ('hot_potato', 'misc'):
			EXTENSION_LOADER.load_extension(extension_name)

	print('Connecting...')
	start_clients()
	try:
		import time
		time.sleep(2000.5)
	except KeyboardInterrupt:
		stop_clients()
		print('Disconnected')
		KOKORO.stop()