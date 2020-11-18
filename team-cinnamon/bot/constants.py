import os
from typing import Dict, Tuple, Union
from hata import discord
import json


with open("config.json") as fp:
    config = json.load(fp)

class Auth:
    BOT_TOKEN: str = os.environ.get("BOT_TOKEN") or config.get("BOT_TOKEN")

class Colors:
    RED = 0xe85133
    GREEN = 0x2cc95e
    BLUE = 0x2cb1c9
