from . import extension
from .. import utils, constants
from hata.discord import client_core
from hata import backend, discord
from time import time

class Fun(extension.Extension):
    def __init__(self, client):
        self.client = client
        self.chat_grabbers = []

    async def send_start_message(self, chat_grabber: utils.ChatGrabber):
        embed = discord.Embed(color=constants.Colors.BLUE, description='Say hi, you\'re talking to people in **{}**'.format(chat_grabber.destination.guild))
        await self.client.message_create(chat_grabber.origin, embed=embed)
        embed = discord.Embed(color=constants.Colors.BLUE, description='Say hi, you\'re talking to people in **{}**'.format(chat_grabber.origin.guild))
        await self.client.message_create(chat_grabber.destination, embed=embed)

    async def send_stop_message(self, chat_grabber: utils.ChatGrabber):
        embed = discord.Embed(color=constants.Colors.BLUE, description='You\'re no longer talking to people in **{}**'.format(chat_grabber.destination.guild))
        await self.client.message_create(chat_grabber.origin, embed=embed)
        embed = discord.Embed(color=constants.Colors.BLUE, description='You\'re no longer talking to people in **{}**'.format(chat_grabber.origin.guild))
        await self.client.message_create(chat_grabber.destination, embed=embed)

    async def create_chat(self, message):
        if any(message.channel in (c.origin, c.destination) for c in self.chat_grabbers):
            await self.client.message_create(message.channel, 'This channel is already chatting.')
            return
        try:
            chat_grabber = next(c for c in self.chat_grabbers if not c.started)
            chat_grabber.set_destination(message.channel)
            await chat_grabber.start()
        except StopIteration:
            embed = discord.Embed(color=constants.Colors.BLUE, description='**Looking for someone who wants to talk to you**')
            await self.client.message_create(message.channel, content=message.author.mention, embed=embed)
            chat_grabber = utils.ChatGrabber(
                self.client, 
                message.channel, 
                timeout=30,
                start_hook=self.send_start_message,
                stop_hook=self.send_stop_message,
                destination_to_origin=True
            )
            self.chat_grabbers.append(chat_grabber)
            backend.future_or_timeout(chat_grabber.destination_future, 30)
            try:
                await chat_grabber.destination_future
            except TimeoutError:
                embed = discord.Embed(color=constants.Colors.RED, description=':x: **No one wants to talk to you**')
                await self.client.message_create(message.channel, content=message.author.mention, embed=embed)
                self.chat_grabbers.remove(chat_grabber)
                return

    async def close_chat(self, message):
        try:
            chat_grabber = next(c for c in self.chat_grabbers if message.channel in (c.origin, c.destination))
        except StopIteration:
            await self.client.message_create(message.channel, 'This channel isn\'t chatting')
            return
        if message.author in chat_grabber.cancellation_votes:
            await self.client.message_create(message.channel, 'You\'ve already voted to close this chat.')
            return
        users = list(filter((lambda key: time() - chat_grabber.users[key]['time'] < 30), chat_grabber.users))
        if message.author.id not in users:
            return
        elif len(chat_grabber.cancellation_votes) >= len(users) - 1:
            await chat_grabber.stop()
            self.chat_grabbers.remove(chat_grabber)
        else:
            chat_grabber.cancellation_votes.append(message.author)
            await self.client.message_create(message.channel, '{}/{} votes required to close this chat.'.format(chat_grabber.cancellation_votes, len(users)))

    @extension.command
    async def chat(self, client, message, arg=None):
        if arg is None:
            await self.create_chat(message)
        elif arg.lower() == 'close':
            await self.close_chat(message)
