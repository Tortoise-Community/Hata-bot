from . import extension
from .. import constants
from .. import utils
from hata import discord
from database import utils as dutils


class Main(extension.Extension):
    def __init__(self, client):
        self.client = client

    @extension.event
    async def ready(self, client):
        print('Logged in as {}'.format(self.client.full_name))

    @extension.command
    async def ping(self, client, message):
        embed = discord.Embed(
            color=constants.Colors.BLUE,
            title='Pong',
            description=':ping_pong: **WebSocket:**'
            ' {:.4f}ms'.format(self.client.gateway.latency * 1000)
        )
        await self.client.message_create(message.channel, embed=embed)

    @extension.command
    async def setlog(self, client, message, channel: discord.ChannelText):
        data = await utils.hata_fut_from_asyncio_task(
            self.client, 
            self.client.get_fetch_or_create(message.guild.id)
        )
        data['log_channel_id'] = channel.id
        await utils.hata_fut_from_asyncio_task(
            self.client,
            dutils.update_guild_setup(
                self.client, 
                guild_id=message.guild.id, 
                log_channel_id=channel.id
            )
        )
        embed = discord.Embed(color=constants.Colors.GREEN, description='Changed log channel to {}'.format(channel.mention))
        await self.client.message_create(message.channel, embed=embed)