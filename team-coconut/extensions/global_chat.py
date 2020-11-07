#import stuff here
#import db

#class chats():
#    
#    async def admin_only_handler(client, message, command, check):
#        await client.message_create(message.channel, f'You must be the owner of the bot to use the `{command}` command.')
#    
#    @Bcom.commands(checks=[checks.admin_only(handler=admin_only_handler)])
#    async def create_chat(self, msg, name):
#        if name has special characters:
#            await client.message_create(message.channel, "sorry that name is invalid please try again")
#            return
#        
#        if there is a table called {name}:
#            await client.message_create(message.channel, "sorry that name is already taken please try again")
#            return
#       
#         if server id in db named {name}:
#            await client.message_create(message.channel, "This server already has a connection to that {name} ")
#            return
#        
#        create table name is {name}
#            primary key = server id
#            #idk anything about database sorryyy
#       
#       await client.message_create(message.channel, "global chat named {name} has been created if you want other server to join your chat do {prefix}request {name} request a join")
#       await pin that message above
#       
#    @Bcom.commands(checks=[checks.admin_only(handler=admin_only_handler)])
#    async def request_chat(self, msg, name):
#        if name not in db:
#            await client.message_create(message.channel, "We dont have a connection named {name} plaese try again ")
#            return
#        if server id in db named {name}:
#            await client.message_create(message.channel, "This server already has a connection to that {name} ")
#            return
#        await client.message_create(name.server.channel, "@admin there is a join request by {msg.author} to join the connection {name} please type accept or decline")
#        
#        if answer == accept:
#            add the server id to the db
#            msg the other server that the request was confirmed and now connected to the server
#            return
#        elif answer == decline:
#            msg the other server that the request was declined and still not connected to the server
#            return
#            
#        if did not answer:
#            msg the other server telling that the admin did not reply
#            return

#    @Bcom.events
#    async def message_create(client, message):
#        if (message.author.is_bot or
#            message.author.is_blacked_listed):
#               return
#            if message in Global chat channel:
#               message.delete()
#               for channel in Db{server_id, channel_id}:
#                   await send that stuff via webhook
#                           