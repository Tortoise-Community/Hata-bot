#original Idea by TheAnonyMouse1337
#import stuff here
#import db

#class call():
#    
#    async def admin_only_handler(client, message, command, check):
#        await client.message_create(message.channel, f'You must be the owner of the bot to use the `{command}` command.')
#    
#    @Bcom.commands(checks=[checks.admin_only(handler=admin_only_handler)])
#    async def register(self, msg):
#        if there is already a registered vc for this server:
#            await client.message_create(message.channel, "you can only register one vc for every guild(for now)")
#            return
#       if not msg.author.is_voice:
#            await client.message_create(message.channel, "you can only register a vc if you are on a vc")
#            return
#        add this vc channel where the user is currently
#        id to db phonelist also add other stuff
#         
#       await client.message_create(message.channel, "the channel {vc channel id} is now registered as the server's Phone. you will receive  phone request calls in #channel")
#       
#    @Bcom.commands()
#    async def contacts(self, msg, vc channel):
#        name=[]
#        for name in db:
#            names.append(name)
#        await send the {name} that can be called in a paginated embed
#    
#    @Bcom.commands()
#    async def search(self, msg, name):
#        if name not in db:
#            await send that name does not exist pls try again
#            return
#        await send here is the name of that vc name to contact do !call {name}
#        
#    @Bcom.commands()
#    async def call(self, msg, vc channel):
#        if not msg.author.is_voice:
#            await client.message_create(message.channel, "you can only call people if you are on a vc")
#            return
#        
#        if not msg.author in registered vc:       
#            await client.message_create(message.channel, "you can only call people if you are on the vc {the registered vc}")
#            return
#            
#        if there is a call on going:
#            await send there is a call on going Right now please try again later
#            return
#        
#        if name not in db:
#            await client.message_create(message.channel, "We cant find {name} plaese try again or check your name input ")
#            return
#      
#        if there is a call on going on the other side:
#            await send there is a call on going on {name} Right now please try again later
#            return
#            
#        await client.message_create(name.server.channel, "@admin there is a join request by {msg.author} to join the connection {name} please type accept or decline") add reaction yes or no
#        
#        on reaction add
#        if author is not on a vc
#            please join a vc first before reacting
#        if author not in registered vc:
#            please join the registered vc first
#        if reaction == accept:
#            join vc
#            return
#        elif reaction == decline:
#            msg the other server that the request was declined and still not connected to the server
#            return
#            
#        if did not answer:
#            msg the other server telling that the admin did not reply
#            return
#   