import json
from hata import discord

class Infraction:
    def __init__(self, client, data):
        self.client = client
        self.dict = data
        self.case_number = data['case_number']
        self.target = discord.User.precreate(int(data['target_id']))
        self.moderator = discord.User.precreate(int(data['moderator_id']))
        self.guild = discord.Guild.precreate(int(data['guild_id']))
        self.reason = data['reason']
        self.pardoned = data['pardoned']
        self.case_type = data['case_type']
        self.cross_guild = data['cross_guild']
        self.extras = json.loads(data['extras'])