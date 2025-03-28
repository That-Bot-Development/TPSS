import discord
from discord.ext import commands

from modules.base import BaseModule

#TODO: Make this configurable through discord instead of hardcoded
class DiscordConstants(BaseModule):
    _instance = None

    # Define as singleton
    def __new__(cls, client):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, client):
        self.client = client

        # Initialize all constants. Defined in define_constants on bot ready call
        self.SERVER = self.CHANNEL_MODMAIL = self.CHANNEL_MISCLOGS = self.CHANNEL_SUGGESTIONS = self.CHANNEL_YOURART = self.ROLE_OWNER = self.ROLE_OWNER = self.ROLE_ADMIN = self.ROLE_MOD = self.ROLE_MMMISC = self.ROLE_COREBOTS = self.VAR_ALLOWEDMENTIONS_NONE = None

    @commands.Cog.listener()
    async def on_ready(self):
        await self.define_constants()

    async def define_constants(self):
        # SERVERS
        self.SERVER = self.client.get_guild(578356230637223936)

        # CHANNELS
        self.CHANNEL_MODMAIL = self.SERVER.get_channel(986085007246381147)
        self.CHANNEL_MISCLOGS = self.SERVER.get_channel(608465315755720714)
        self.CHANNEL_SUGGESTIONS = self.SERVER.get_channel(1037952455188693042)
        self.CHANNEL_YOURART = self.SERVER.get_channel(579313588972552193)

        # ROLES
        self.ROLE_OWNER = self.SERVER.get_role(578357103144468490)
        self.ROLE_ADMIN = self.SERVER.get_role(578356923611611146)
        self.ROLE_MOD = self.SERVER.get_role(624816689393041425)
        self.ROLE_MMMISC = self.SERVER.get_role(987189009656733696)
        self.ROLE_COREBOTS = self.SERVER.get_role(897306192555151411)

        #MISC
        self.VAR_ALLOWEDMENTIONS_NONE = discord.AllowedMentions(everyone=False,users=False,roles=False,replied_user=False)

    @classmethod
    def get(cls):
        return DiscordConstants._instance

