from databases.shared_data import common_data
from hata import Client, Message, Guild, ChannelText, User, eventlist
from hata.ext.commands import Command

Reimu: Client
CHAT_COMMANDS = eventlist(type_=Command)


def setup(lib):
    category = Reimu.command_processer.get_category('CHAT')
    if not category:
        Reimu.command_processer.create_category('CHAT', )

    Reimu.commands.extend(CHAT_COMMANDS)


def teardown(lib):
    Reimu.commands.unextend(CHAT_COMMANDS)


@CHAT_COMMANDS.from_class
class connect:
    """
    Connects the current channel to any other channel in any other server
    Usage - **`connect [channel mention or id] <guild>`**
    """
    category = 'CHAT'

    async def command(client: Client, message: Message, channel: ('int', 'channel'), guild: Guild = None):
        initial_webhook = await client.webhook_get_channel(message.channel)
        if guild is None:
            guild = message.guild
        if not isinstance(channel, ChannelText):
            channel = guild.channels.get(channel)
        if not isinstance(channel, ChannelText):
            return await client.message_create(message.channel, f'Unknown Channel in guild {guild.name}')
        if message.channel.id in common_data:
            other = common_data[message.channel.id]["other"]
            if other.guild is message.guild:
                return await client.message_create(message.channel, f'You already connected to {other.mention}')
            return await client.message_create(message.channel,
                                               f'You already connected to {other.mention} in **`{other.guild}`**')
        if channel.id in common_data:
            return await client.message_create(message.channel,
                                               f'{channel.mention} is already connected to another channel')
        if message.channel is channel:
            return await client.message_create(message.channel, 'You must provide a different channel')
        if initial_webhook:
            initial_webhook = initial_webhook[0]
        else:
            initial_webhook = await client.webhook_create(message.channel, 'Coconuts')
        final_webhook = await client.webhook_get_channel(channel)
        if final_webhook:
            final_webhook = final_webhook[0]
        else:
            final_webhook = await client.webhook_create(channel, 'Coconuts')
        common_data[message.channel.id] = {}
        common_data[message.channel.id]['webhook'] = final_webhook
        common_data[message.channel.id]['other'] = channel
        common_data[channel.id] = {}
        common_data[channel.id]['webhook'] = initial_webhook
        common_data[channel.id]['other'] = message.channel
        if channel.guild is message.guild:
            await client.message_create(message.channel, f'Connected to {channel.mention}')
            return await client.message_create(channel, f'Connected to {message.channel.mention}')
        await client.message_create(message.channel, f'Connected to {channel.mention} in **`{channel.guild.name}`**')
        await client.message_create(channel, f'Connected to {message.channel.mention} in **`{message.guild.name}`**')


@CHAT_COMMANDS.from_class
class disconnect:
    """
    Disconnects the current channel from all other channel connections
    Usage - **`disconnect`**(no other parameters)
    """
    category = 'CHAT'

    async def command(client: Client, message: Message):
        if message.channel.id not in common_data:
            return await client.message_create(message.channel, 'There isn\'t a connection in this channel')
        other = common_data[message.channel.id]['other']
        if other.guild is message.guild:
            await client.message_create(message.channel, f'Disconnected from {other.mention}')
            await client.message_create(other, f'Disconnected from {message.channel.mention}')
        else:
            await client.message_create(other,
                                        f'Disconnected from {message.channel.mention} in `**{message.guild.name}**`')
            await client.message_create(message.channel,
                                        f'Disconnected from {other.mention} in `**{other.guild.name}**`')
        del common_data[other.id]
        del common_data[message.channel.id]


@CHAT_COMMANDS.from_class
class chatmute:
    """
    Blocks the given user from using the global chat
    Usage - **`chatmute [user mention or id]`**
    """
    category = 'CHAT'

    async def command(client: Client, message: Message, user: User):
        if common_data.get('muted') is None:
            common_data['muted'] = []
        common_data['muted'].append(user.id)
        await client.message_create(message.channel, f'Muted {user.mention}')


@CHAT_COMMANDS.from_class
class chatunmute:
    """
    Unblocks the given user for using the global chat
    Usage - **`chatunmute [user mention or id]`**
    """
    category = 'CHAT'

    async def command(client: Client, message: Message, user: User):
        if common_data.get('muted') is None:
            common_data['muted'] = []
        if user.id in common_data['muted']:
            common_data['muted'].remove(user.id)
        await client.message_create(message.channel, f'Unmuted {user.mention}')
