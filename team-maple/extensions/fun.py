import cv2
import numpy as np
import random
from hata.discord import CLIENTS
from hata import ReuBytesIO
from PIL import Image
Inosuke = CLIENTS[773778938405191680]
Zenitsu = CLIENTS[774156784189046804]

@Zenitsu.commands(aliases=['emboss', 'ruin'], description="Emboss a user's pfp")
async def emb(client, message, user: 'user'=None):
    user = user
    if user is None:
        async with client.http.get(message.author.avatar_url_as(size=1024)) as resp:
            pfp_by = np.asarray(bytearray(await resp.read()), dtype="uint8")
        pfp = cv2.imdecode(pfp_by, cv2.IMREAD_COLOR)

    else:
        async with client.http.get(user.avatar_url_as(size=1024)) as resp:
            pfp_by = np.asarray(bytearray(await resp.read()), dtype="uint8")
        pfp = cv2.imdecode(pfp_by, cv2.IMREAD_COLOR)
    kernel = np.array([[0,-1,-1],
                        [1,0,-1],
                        [1,1,0]])
    rng = cv2.filter2D(pfp, -1, kernel)
    with ReuBytesIO() as buffer:
        img = Image.fromarray(rng)
        img.save(buffer, 'png')                   
        buffer.seek(0)
        await client.message_create(message.channel, file=('this_is_comp_emboss.png', buffer))  
        inosuke_resps = ['That looks like poop lmao',
        'Nice work Zenitsu on making it look like trash lmfao',
        'Wtf is that even bwaahaha',
        f'It turned out exactly as I expected LOL']
        
        zenitsu_resps = ['D:', 'awww why I worked so hard on it T-T',
        'https://tenor.com/view/zenitsu-crying-frustrated-sad-tears-gif-14992860']

        await Inosuke.message_create(message.channel, random.choice(inosuke_resps)) 
        await client.message_create(message.channel, random.choice(zenitsu_resps))
