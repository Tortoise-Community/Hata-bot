#pylint:disable=E0213
import hata
from hata import eventlist, Message, Client, UserBase, ChannelBase, Guild, Role, Embed
from hata.ext.commands import Command

INFO_COMMANDS = eventlist(type_=Command)
Bcom: Client

def setup(lib):
    category = Bcom.command_processer.get_category("info")
#    if not category:
#        Bcom.command_processer.get_category("INFO")
    Bcom.commands.extend(INFO_COMMANDS)

def teardown(lib):
    Bcom.commands.unextend(INFO_COMMANDS)

#@INFO_COMMANDS.from_class
#class user_info:
#    category = 'info'

#    async def command(client: Client, message: Message):
#        """Gives you information about a user"""

@INFO_COMMANDS.from_class
class bot_info:
    category = 'info'

    async def command(client: Client, message: Message):
        """Gives you information about the bot"""

#@INFO_COMMANDS.from_class
#class server_info:
#    category = 'info'

#    async def command(client: Client, message: Message):
#        """Gives you information about a server"""
#        pass

@INFO_COMMANDS.from_class
class what_is:
    category = 'info'

    async def command(client, message, entity: ('user', 'channel', 'role') = None):
        """Tells you what an Id or a name is preferably used with Ids"""
        if entity is None:
            result = 'Idk what that thing is UwU'
        elif isinstance(entity, UserBase):
            if entity.is_bot:
                result = 'That user us a bot'
            else:
                result = "That user is a human"
        elif isinstance(entity, ChannelBase):
            result = 'That thing is a channel'
        else:
            result = 'That thing is a role'
    
        await client.message_create(message.channel, result)

@INFO_COMMANDS.from_class
class seek_info:
    category = 'info'

    async def command(client, message, entity: ('user', 'channel', "guild",'role') = None):
        """Tells you about that thing when it was made or anything else"""
        
        if entity is None:
            entity = message.author
        
        embed = Embed()
        #use this if you can't find what the thing is
        async def cantfind():
            pass

        #if can't be found on other server use this to search and use other bots UwU
         
        async def userinfo(embed):
           #______
            embed.add_author(name=message.author.name)
            embed.add_thumbnail(url=entity.avatar_url)
            name = 'User INFO Global'
            fields = [
                    ['ID', entity.id],
                    ['Account Created At', entity.created_at]
                ]
            field = ''
            for x, y in fields:
                field += f'**{x}** - {y}\n'
            if entity.is_bot:
                description = 'Bot'
            else:
                description = 'User'
            field += f'**User Type** - {description}\n'
            embed.add_field(name=name, value=field, inline=False)
                
            name = 'User INFO in Guild'
            fields = [
                    ['User Joined Server At', entity.guild_profiles[message.guild].joined_at],
                    ['Nickname', entity.guild_profiles[message.guild].nick],
#                    ['Date User Boosted Server',entity.premium_since],
                    ['Roles', x if (x := '  '.join(r.mention for r in entity.guild_profiles[message.guild].roles[1:])) else None],
                    ['Highest Role In Server', x[-1].mention if (x := entity.guild_profiles[message.guild].roles[1:]) else None]
                ]
            field = ''
            for x, y in fields:
                field += f'**{x}** - {y}\n'
            embed.add_field(name=name, value=field, inline=False)
                
            if entity.activities:
                for activity in entity.activities:
                    if isinstance(entity.status, hata.discord.activity.ActivityBase):
                        name = 'Activity'
                        fields = [
                                ['Activity Name', (x if (x := activity.emoji) else '') + activity.name],
                                ['ID', activity.application_id],
                                ['Link', activity.url],
                                ['State', activity.state],
                                ['Details', activity.details],
                                ['Started at', activity.start],
                                ['Ended at', activity.end],
                            ]
                        field = ''
                        for x, y in fields:
                            field += f'**{x}** - {y}\n'
                        embed.add_field(name=name, value=field, inline=False)
                 #   elif isinstance(activity, discord.Game):
#                        name = 'Game'
#                        fields = [
#                            ['Name', activity.name],
#                            ['Started at', activity.start],
#                            ['Ended at', activity.end],
#                            ]
#                        field = ''
#                        for x, y in fields:
#                           field += f'**{x}** - {y}\n'
#                        embed.add_field(name=name, value=field, inline=False)
#                    elif isinstance(activity, discord.Streaming):
#                        name = 'Streaming'
#                        fields = [
#                                ['Streaming place', activity.platform],
#                                ['Details', activity.details],
#                                ['Game', activity.game],
#                                ['Link', activity.url],
#                                ['Name of User in Twitch', activity.twitch_name]
#                           ]
#                        field = ''
#                        for x, y in fields:
#                            field += f'**{x}** - {y}\n'
#                        embed.add_field(name=name, value=field, inline=False)
                            
                    #elif isinstance(activity, discord.CustomActivity):
#                        name = 'Custom Activity'
#                        fields = [
#                                ['Name', (x if (x := activity.emoji) else '') + activity.name]
#                            ]
#                            field = ''
#                            for x, y in fields:
#                                field += f'**{x}** - {y}\n'
#                            embed.add_field(name=name, value=field, inline=False)
#                return embed
               #______
               
               
        #info on that guild if not found then... say idk
        async def guildinfo():
        #    owner
#            region
#            boost
#            categories
#            text channels count
#            voice channels Count
#            entitys
#            roles
            pass

        #can be found in..?
        async def channelinfo():
#            where can be found
#            what channel type with lock = bool
#            what role can access
#            under what category
            pass
        
        #how many people can use this role
        async def roleinfo():
            #where is this role can be found(server)
#            when it is made
#            what color
#            how many people have this role
#            what perms does it have
            pass
        
        if isinstance(entity, UserBase):
            await userinfo(embed)
        
        elif isinstance(entity, ChannelBase):
            await channelinfo(embed)
        
        elif isinstance(entity, Guild):
            await guildinfo(embed)
        
        elif isinstance(entity, Role):
            await roleinfo(embed)
        
        else:
            await cantfind(embed)
            
        await client.message_create(message.channel, embed=embed)
