import asyncio
import json
from logging import getLogger
from importlib import import_module
import hata
from hata.discord import client_core
from hata import discord
from hata.ext import commands
from database import utils
from . import constants

log = getLogger(__name__)


@hata.backend.KeepType(discord.Client)
class Client:
    ready_event = asyncio.Event()
    _asyncio_event_loop = asyncio.get_event_loop()
    extensions = []
    cached_guild_setups = {}

    def load_extension(self, ext):
        for method in ext._methods:
            method._load(ext, self)
        ext.__init__(self, *ext._args_, **ext._kwargs_)
        self.extensions.append(ext)
        return ext

    async def _ready_set(self, _):
        self._asyncio_event_loop.call_soon_threadsafe(self.ready_event.set)

    async def _add_guild_on_create(self, _, guild):
        asyncio.run_coroutine_threadsafe(self.get_fetch_or_create(guild.id), loop=self._asyncio_event_loop)

    async def _get_guild_setups(self):
        execute = """
            SELECT * FROM guilds
        """
        conn = self.database.conn
        setups = await conn.fetch(execute)
        for setup in setups:
            self._add_guild_setup(dict(setup))

    def _add_guild_setup(self, setup):
        setup['guild_id'] = int(setup['guild_id'])
        if setup['log_channel_id'] is not None:
            setup['log_channel_id'] = int(setup['log_channel_id'])
        if setup['muted_role_id'] is not None:
            setup['muted_role_id'] = int(setup['muted_role_id'])
        setup['disabled_commands'] = json.loads(setup['disabled_commands'])
        setup['prefixes'] = json.loads(setup['prefixes'])
        setup['level_roles'] = json.loads(setup['level_roles'])
        setup['join_roles'] = json.loads(setup['join_roles'])
        self.cached_guild_setups[setup['guild_id']] = setup

    async def _create_guild_setups(self, get_after=True):
        await self.database.wait_until_ready()
        await self.ready_event.wait()
        await self._get_guild_setups()
        for guild in hata.discord.GUILDS:
            if guild not in self.cached_guild_setups:
                await utils.post_guild_setup(self, guild_id=guild)
        await self._get_guild_setups()

    def get_guild_setup(self, guild_id):
        return self.cached_guild_setups.get(int(guild_id))

    async def fetch_guild_setup(self, guild_id):
        data = await utils.get_guild_setup(self, guild_id=guild_id)
        if data:
            self._add_guild_setup(data)
        return data

    async def get_fetch_or_create(self, guild_id):
        data = self.get_guild_setup(guild_id)
        if data:
            return data
        data = await self.fetch_guild_setup(guild_id)
        if data:
            return data
        await utils.post_guild_setup(self, guild_id=guild_id)
        data = await self.fetch_guild_setup(guild_id)
        return data

    async def _get_prefix(self, message):
        if message.guild is None:
            return '!'
        data = await self.get_fetch_or_create(message.guild.id)
        for prefix in data['prefixes']:
            if message.content.startswith(prefix):
                return prefix
        return data['prefixes'][0]

    def login(self, *, db=True, client=True, server=True):
        if client:
            self.events(self._ready_set, name='ready')
            self.events(self._add_guild_on_create, name='guild_create')
            self.start()
        if server:
            self._asyncio_event_loop.create_task(self.server.start())
        if db:
            self._asyncio_event_loop.create_task(self.database.connect())
        if db and client:
            self._asyncio_event_loop.create_task(self._create_guild_setups())
        try:
            log.debug('Logged in, starting asyncio event loop')
            self._asyncio_event_loop.run_forever()
        except KeyboardInterrupt:
            log.debug('Received KeyboardInterrupt, stopping processes')
            self.stop()
            discord.client_core.KOKORO.stop()
            exit()
