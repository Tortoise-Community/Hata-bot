from databases.shared_data import common_data
from hata import eventlist, Message, Client
from hata.ext.commands import Command
from utils.utils import setdefault

CALL_COMMANDS = eventlist(type_=Command)
Reimu: Client


def setup(lib):
    category = Reimu.command_processer.get_category('Call')
    if not category:
        Reimu.command_processer.create_category('Call', )

    Reimu.commands.extend(CALL_COMMANDS)


def teardown(lib):
    Reimu.commands.unextend(CALL_COMMANDS)


@CALL_COMMANDS.from_class
class register:
    category = 'Call'

    async def command(client: Client, message: Message):
        setdefault(common_data, 'ServerCallChannel', {})
        voice_client = client.voice_client_for(message)
        if voice_client is None:
            voice_client = message.guild.voice_states.get(message.author.id, None)
        setdefault(common_data['ServerCallChannel'], message.guild.id, {})
        guild_data = common_data['ServerCallChannel'][message.guild.id]
        guild_data['VoiceID'] = voice_client.channel.id
        guild_data['ChannelID'] = message.channel.id

        msg = f"The voice channel **`{voice_client.channel.name}`** is now registered as the server's Phone. you will receive phone request calls in {message.channel.mention}"
        await client.message_create(message.channel, msg)


@CALL_COMMANDS.from_class
class getdata:
    async def command(client: Client, message: Message):
        await client.message_create(message.channel, f"```\n{common_data.get('ServerCallChannel', {})}\n```")
