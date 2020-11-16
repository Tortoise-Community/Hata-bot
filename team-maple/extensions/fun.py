import cv2
import numpy as np
import random
import hata.ext.asyncio
import async_cleverbot as ac
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
        'https://tenor.com/view/zenitsu-crying-frustrated-sad-tears-gif-14992860',
        'https://tenor.com/view/zenitsu-demon-slayer-kimetsu-no-yaiba-manga-series-smh-gif-17682808',
        'https://tenor.com/view/kimetsu-no-yaiba-zenitsu-scared-scary-demon-slayer-gif-15951499']

        await Inosuke.message_create(message.channel, random.choice(inosuke_resps)) 
        await client.message_create(message.channel, random.choice(zenitsu_resps))

z_resps = ['Hi there..', 'Hello', 'Hi Inosuke']
i_resps = ['Wtf are you doing here!', 'Hi...', 'Hi Weakling']
toggle = False
@Zenitsu.commands(aliases=['chat', 'ch', 'interact'], description='Start a conversation between inosuke and zenitsu')
async def talk(client, message, signal=None):
    global toggle
    signal = signal
    if signal is None or signal.lower() in ('start', 'go'):
        toggle = True
        if random.randint(0, 1) == 0:
            await client.message_create(message.channel, random.choice(z_resps))
        else:
            await Inosuke.message_create(message.channel, random.choice(i_resps))
    elif signal.lower() in ('stop', 'shutup', 'shut'):
        toggle = False
    

@Inosuke.events
async def message_create(client, message):
    if message.author is client:
        return
    if toggle:
        if message.author is Zenitsu:
            with client.keep_typing(message.channel):
                cleverbot = ac.Cleverbot("+2nmi](^0op9:uPGmJr2")
                response = await cleverbot.ask(message.content, emotion=ac.Emotion.anger)
                await client.message_create(message.channel, response.text)
                await cleverbot.close()

@Zenitsu.events
async def message_create(client, message):
    if message.author is client:
        return
    if toggle:
        if message.author is Inosuke:
            with client.keep_typing(message.channel):                
                cleverbot = ac.Cleverbot("+2nmi](^0op9:uPGmJr2")
                response = await cleverbot.ask(message.content, emotion=ac.Emotion.scared)
                await client.message_create(message.channel, response.text)
                await cleverbot.close()