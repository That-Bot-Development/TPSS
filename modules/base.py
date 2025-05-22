import discord
from discord.ext import commands

from modules.util.sql_manager import SQLManager
from modules.util.discord_const import DiscordConstants


class BaseModule(commands.Cog):
    # "Global" items that all modules should be able to access
    client:discord.Client = None
    bot_started = False
    version = "2.8.0" # Move to config, add getter
    d_consts:DiscordConstants = None
    sql:SQLManager = None


    def __init__(self, client):
        self.client = client

    async def get_member(self, user_id) -> discord.Member: # TODO: Should this even be here? NO neither should the thing below...
        server:discord.Guild = self.d_consts.SERVER
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