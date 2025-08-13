import discord
from discord.ext import commands

from bot_client import Client
from modules.util.sql_manager import SQLManager
from modules.util.discord_const import DiscordConstants

async def setup(client:Client, config):
    await client.add_cog(BaseModule(client, config))

class BaseModule(commands.Cog):

    def __init__(self, client:Client, config=None):
        # Load config 
        if config:
            config = config

        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        pass

    async def get_member(self, user_id) -> discord.Member: # TODO: Should this even be here? NO neither should the thing below...
        server:discord.Guild = self.client.d_consts.SERVER
        try:
            return server.get_member(user_id) or await server.fetch_member(user_id)
        except Exception:
            raise MemberNotFoundError("Member could not be found.")
        
    def truncate_string(self, text, max_length=16):
        """Truncates a string and adds ellipsis if it exceeds max_length."""

        if len(text) > max_length:
            return text[:max_length] + "..."
        return text

class MemberNotFoundError(Exception):
    """Thrown when the a discord member cannot be found."""
    pass