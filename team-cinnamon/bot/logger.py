from hata import discord
from . import utils

class Logger:
    def __init__(self, client):
        self.client = client

    async def log(self, guild, *args, **kwargs):
        data = await utils.hata_fut_from_asyncio_task(
            self.client, 
            self.client.get_fetch_or_create(guild.id)
        )
        channel_id = data['log_channel_id']
        if channel_id is None:
            return
        channel = discord.ChannelText.precreate(channel_id)
        message = await utils.try_send(self.client, channel, *args, **kwargs)
        return message
