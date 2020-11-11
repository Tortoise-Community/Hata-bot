from databases.shared_data import common_data
from hata import eventlist, Message, Client, ChannelVoice, ChannelText, ReactionAddEvent, BUILTIN_EMOJIS
from hata.ext.commands import Command, utils
from utils.utils import setdefault, MixerStream

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
        setdefault(common_data, 'CallRegisterData', {})
        voice_client = client.voice_client_for(message)
        if voice_client is None:
            voice_client = message.guild.voice_states.get(message.author.id, None)
        guild_data = setdefault(common_data['CallRegisterData'], message.guild.id, {})
        guild_data['VoiceID'] = voice_client.channel.id
        guild_data['ChannelID'] = message.channel.id
        guild_data['UserID'] = message.author.id

        msg = f"The voice channel **`{voice_client.channel.name}`** is now registered as the server's Phone. you will receive phone request calls in {message.channel.mention}"
        msg += f'\n**{message.guild.id}** is your phone number'
        await client.message_create(message.channel, msg)


def check(_id, event: ReactionAddEvent):
    if _id == event.user.id and event.emoji in [BUILTIN_EMOJIS['white_check_mark'], BUILTIN_EMOJIS['x']]:
        return True
    return False


@CALL_COMMANDS.from_class
class call:
    category = 'Call'

    async def command(client: Client, message: Message, number: 'int'):
        if message.guild.id not in common_data.get('CallRegisterData', {}).keys():
            return await client.message_create(message.channel, 'Register this server first by typing `r1register`')
        if number not in common_data.get('CallRegisterData', {}).keys():
            return await client.message_create(message.channel, f'Number {number} not found')
        if number == message.guild.id:
            return await client.message_create(message.channel, f'Call someone other than yourself')
        await client.message_create(message.channel, f'Attempting to call {number}')
        data = common_data['CallRegisterData']
        other_voice = ChannelVoice.precreate(data[number]['VoiceID'])
        my_voice = ChannelVoice.precreate(data[message.guild.id]['VoiceID'])
        other_channel = ChannelText.precreate(data[number]['ChannelID'])
        other_message = await client.message_create(other_channel,
                                                    f"<@{data[number]['UserID']}>" + f' incoming call from {message.guild.id}')
        await client.reaction_add(other_message, BUILTIN_EMOJIS['white_check_mark'])
        await client.reaction_add(other_message, BUILTIN_EMOJIS['x'])
        try:
            res = await utils.wait_for_reaction(client, other_message, lambda x: check(data[number]['UserID'], x), 60)
        except TimeoutError:
            await client.reaction_clear(other_message)
            await client.message_create(other_channel, 'Call got timed out')
            return await client.message_create(message.channel,
                                               message.author.mention + ', Your call wasn\'t picked up')
        if res.emoji == BUILTIN_EMOJIS['white_check_mark']:
            await client.reaction_clear(other_message)
            await client.message_create(other_channel, 'Call Accepted')
            await client.message_create(message.channel, message.author.mention + ', Your call was accepted')
        else:
            await client.reaction_clear(other_message)
            await client.message_create(other_channel, 'Call Declined')
            return await client.message_create(message.channel, message.author.mention + ', Your call was declined')

        vc1 = await client.join_voice_channel(other_voice)
        vc2 = await client.join_voice_channel(my_voice)

        mixer = MixerStream()
        for user in other_voice.voice_users:
            if user is client:
                continue

            source = vc1.listen_to(user, yield_decoded=True)
            await mixer.add(source)
        vc2.append(mixer)

        mixer = MixerStream()
        for user in other_voice.voice_users:
            if user is client:
                continue

            source = vc2.listen_to(user, yield_decoded=True)
            await mixer.add(source)
        vc1.append(mixer)
        data = setdefault(common_data, 'CallData', {})
        data[message.guild.id] = {'Other': number, 'OtherVC': vc1, 'SelfVC': vc2, 'SelfChannel': my_voice}
        data[number] = {'Other': message.guild.id, 'OtherVC': vc2, 'SelfVC': vc1, 'SelfChannel': other_voice}


@CALL_COMMANDS.from_class
class getdata:
    async def command(client: Client, message: Message):
        await client.message_create(message.channel, f"```\n{common_data.get('CallRegisterData', {})}\n```")
