from audioop import add as add_voice

import config
from hata import Client, Message, ChannelVoice
from hata.discord.opus import OpusDecoder
from hata.discord.player import AudioSource
from hata.ext.commands import setup_ext_commands
from hata.ext.commands.content_parser import FlaggedAnnotation, ConverterFlag
from hata.ext.commands.helps.subterranean import SubterraneanHelpCommand

Astra: Client
setup_ext_commands(Astra, config.ASTRA_PREFIX)
Astra.commands(SubterraneanHelpCommand(), 'help')


async def _join(client: Client, message: Message):
    voice_client = client.voice_client_for(message)
    if voice_client is None:
        voice_client = await client.join_voice_channel(message.guild.voice_states.get(message.author.id, None).channel)
    return voice_client


@Reimu.commands
async def join(client: Client, message: Message):
    await _join(client, message)


@Reimu.commands
async def play_from(client, message, voice_channel: FlaggedAnnotation(ChannelVoice, ConverterFlag.channel_all)):
    while True:
        self_guild = message.guild
        if self_guild is None:
            text = 'Not in guild.'
            break

        other_guild = voice_channel.guild
        if other_guild is None:
            text = 'Other channel not in guild.'
            break

        self_voice_client = client.voice_client_for(message)
        if self_voice_client is None:
            voice_state = self_guild.voice_states.get(message.author.id, None)
            if voice_state is None:
                text = 'You are not at a voice channel.'
                break

            self_channel = voice_state.channel
            if not self_channel.cached_permissions_for(client).can_connect:
                text = 'I have no permissions to connect to that channel'
                break

            try:
                self_voice_client = await client.join_voice_channel(self_channel)
            except TimeoutError:
                text = 'Timed out meanwhile tried to connect.'
                break
            except RuntimeError:
                text = 'The client cannot play voice, some libraries are not loaded'
                break

        other_voice_states = list(other_guild.voice_states.values())
        for voice_state in other_voice_states:
            if voice_state.user is not client:
                break
        else:
            text = 'No voice states in other guild.'
            break
        try:
            other_voice_client = client.voice_clients[other_guild.id]
        except KeyError:
            try:
                other_voice_client = await client.join_voice_channel(voice_channel)
            except TimeoutError:
                text = 'Timed out meanwhile tried to connect.'
                break
            except RuntimeError:
                text = 'The client cannot play voice, some libraries are not loaded'
                break

        mixer = MixerStream()
        for voice_state in other_voice_states:
            user = voice_state.user
            if user is client:
                continue

            source = other_voice_client.listen_to(user, yield_decoded=True)
            await mixer.add(source)

        if self_voice_client.append(mixer):
            text = f'Now playing {mixer.title}!'
        else:
            text = f'Added to queue {mixer.title}!'
        break

    await client.message_create(message.channel, text)
