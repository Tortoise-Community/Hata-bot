import time


from dotenv import load_dotenv
load_dotenv()
from hata.discord import KOKORO, start_clients, stop_clients, Client


from config import CLIENT_INFO
from misc import setup as setup_misc
from hot_potato import setup as setup_hot_potato



async def ready(client: Client):
	# TODO - output info for client
	print(f'{client:f} logged in.')

if __name__ == '__main__':
	for info in CLIENT_INFO.values():
		client = info['CLIENT']
		client.events(ready)
		setup_hot_potato(client, info)
		setup_misc(client, info)

	print('Connecting...')
	start_clients()
	try:
		import time
		time.sleep(2000.5)
	except KeyboardInterrupt:
		stop_clients()
		print('Disconnected')
		KOKORO.stop()