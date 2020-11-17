import asyncio
import json
from aiohttp import web

from . import constants
from database import constants as db_constants

class Server(web.Application):
    def __init__(self, client, *args, **kwargs):
        self.client = client
        super().__init__(*args, **kwargs)
        self.add_routes([
            web.get('/', self.index),
            web.get('/documentation', self.index),
            web.get('/index.js', self.index_js),

            web.get('/scripts/jquery.js', self.jquery),

            web.get('/header/header.html', self.header),
            web.get('/header/header.css', self.header_css),

            web.get('/home/home.html', self.home),
            web.get('/home/home.css',  self.home_css),

            web.get('/documentation/documentation.html', self.documentation),
            web.get('/documentation/documentation.css', self.documentation_css),

            web.get('/assets/cinnamon.png', self.cinnamon),
        ])

    async def index(self, request: web.Request):
        return web.Response(body=constants.Index.HTML, content_type='text/html')

    async def index_js(self, request: web.Request):
        return web.Response(body=constants.Index.JAVASCRIPT, content_type='text/javascript')

    async def jquery(self, request: web.Request):
        return web.Response(body=constants.Scripts.JQUERY, content_type='text/javascript')

    async def header(self, request: web.Request):
        return web.Response(body=constants.Header.HTML, content_type='text/html')

    async def header_css(self, request: web.Request):
        return web.Response(body=constants.Header.CSS, content_type='text/css')

    async def home(self, request: web.Request):
        return web.Response(body=constants.Home.HTML, content_type='text/html')

    async def home_css(self, request: web.Request):
        return web.Response(body=constants.Home.CSS, content_type='text/css')

    async def documentation(self, request: web.Request):
        return web.Response(body=constants.Documentation.HTML, content_type='text/html')

    async def documentation_css(self, request: web.Request):
        return web.Response(body=constants.Documentation.CSS, content_type='text/css')

    async def cinnamon(self, request: web.Request):
        return web.Response(body=constants.Assets.CINNAMON, content_type='image/png')

    async def start(self):
        await web._run_app(self, **constants.WebApp.SERVER_SETUP)