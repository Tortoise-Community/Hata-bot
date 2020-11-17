import asyncpg
import asyncio
from logging import getLogger
from hata.discord.client_core import KOKORO
from hata.backend import Future

from . import constants

log = getLogger(__name__)

class Database:
    def __init__(self, client):
        self.client = client
        self.conn = None

        self.lock = asyncio.Lock()
        self._ready_event = asyncio.Event()

    def wait_until_ready(self):
        return self._ready_event.wait()

    async def connect(self) -> None:
        self.conn = await asyncpg.connect(**constants.Auth.DATABASE_SECRETS)
        log.debug('Created connection to database')

        async with self.lock:
            with open('database/schema.sql') as fp:
                await self.conn.execute(fp.read())

        self._ready_event.set()