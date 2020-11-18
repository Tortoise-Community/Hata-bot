import aiohttp
import asyncio

JQUERY_URL = 'https://code.jquery.com/jquery-3.5.1.js'


with open('website/scripts/jquery.js', 'w+') as fp:
    if not fp.read():
        async def fetch():
            async with aiohttp.ClientSession().get(JQUERY_URL) as req:
                fp.write(await req.text())
                req.close()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(fetch())