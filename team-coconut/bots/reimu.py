import config
from databases.shared_data import common_data
from hata import Client, Message, Guild, ChannelText
from hata.discord.exceptions import DiscordException
from hata.ext.commands import setup_ext_commands
from hata.ext.commands.helps.subterranean import SubterraneanHelpCommand
from utils.utils import colourfunc, send

Reimu: Client
setup_ext_commands(Reimu, config.REIMU_PREFIX)
Reimu.commands(SubterraneanHelpCommand(color=colourfunc), name='help')


@Reimu.commands(aliases={'getmsg'})
async def getmessage(client: Client, message: Message, msg: ('int', 'str') = None,
                     channel: ('int', 'channel') = None, guild: Guild = None):
    """
    Gets the message from any server via id or link
    Usage - **`getmessage [message id or link] <channel id> <server id>`**

    Alias - `getmsg`
    """
    if isinstance(msg, str):
        if msg.strip().startswith('http'):
            msg = msg.split('/')
            guild = Guild.precreate(int(msg[4]))
            channel = int(msg[5])
            msg = int(msg[6])
    if msg is None:
        msg = message.id
        channel = message.channel.id
        guild = message.guild
    elif channel is None:
        channel = message.channel.id
        guild = message.guild
    elif guild is None:
        guild = message.guild
    if not isinstance(guild, Guild):
        return await client.message_create(message.channel, 'Unknown Guild')
    if not isinstance(channel, ChannelText):
        channel = guild.channels.get(channel)
    if not isinstance(channel, ChannelText):
        return await client.message_create(message.channel, f'Unknown Channel in guild {guild.name}')
    try:
        content = await client.message_get(channel, msg)
    except DiscordException:
        return await client.message_create(message.channel, f'Unknown Message in channel {channel.name}')
    print(message.author.id)
    await client.message_create(message.channel, content.content)


@Reimu.events
async def message_create(client: Client, message: Message):
    if message.author.is_bot:
        return
    if message.channel.id in common_data:
        if common_data.get('muted') is None:
            common_data['muted'] = []
        if message.content.startswith(client.command_processer.prefix):
            return
        if message.author.id not in common_data['muted']:
            await send(client, common_data[message.channel.id]['webhook'], message)
