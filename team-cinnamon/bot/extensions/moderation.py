from . import extension
from .. import utils
from .. import constants
from database import utils as dutils
from hata import discord
from hata import backend

class Moderation(extension.Extension):
    def __init__(self, client):
        self.client = client

    @extension.command
    async def ban(self, client, message, user: discord.User, reason=None):
        if reason is None:
            reason = 'No reason provided'
        infraction = await utils.hata_fut_from_asyncio_task(
            self.client,
            dutils.post_infraction(
                self.client, guild_id=message.guild.id,
                target_id=user.id, 
                moderator_id=message.author.id,
                reason=reason, case_type='ban',
            )
        )
        banned_embed = utils.procude_infraction_embed(
            case_number=infraction.case_number, 
            what_happened='You were banned from {}'.format(message.guild),
            case_type=infraction.case_type, reason=reason, 
            moderator=message.author
        )
        log_embed = utils.procude_infraction_embed(
            case_number=infraction.case_number, 
            what_happened='{0.full_name} (ID: {0.id})'.format(user),
            case_type=infraction.case_type, reason=reason, 
            moderator=message.author
        )
        dm = await utils.try_create_dm(self.client, user)
        if dm is not None:
            await utils.try_send(self.client, user, embed=banned_embed)
        await self.client.logger.log(message.guild, embed=log_embed)
        try:
            await self.client.guild_ban_add(
                guild=message.guild, 
                user=user,
                reason=reason
            )
            embed = discord.Embed(
                color=constants.Colors.GREEN,
                description='Successfully banned {}'.format(user.full_name)
            )
        except discord.DiscordException as e:
            infraction = await utils.hata_fut_from_asyncio_task(
                self.client,
                dutils.pardon_infraction(
                    self.client,
                    guild_id=message.guild.id,
                    target_id=user.id,
                    moderator_id=self.client.id,
                    reason='Failed to ban (Error: {})'.format(e),
                    case_number=infraction.case_number
                )
            )
            log_embed = utils.procude_infraction_embed(
                case_number=infraction.case_number, 
                what_happened='{0.full_name} (ID: {0.id})'.format(user),
                case_type=infraction.case_type, 
                reason=infraction.reason, 
                moderator=message.author
            )
            embed = discord.Embed(
                color=constants.Colors.RED,
                description=infraction.reason
            )
            await self.client.logger.log(message.guild, embed=log_embed)
        await self.client.message_create(message.channel, embed=embed)