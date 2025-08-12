import discord
from discord.ext import commands

from modules.util.sql_manager import SQLManager
from modules.util.discord_const import DiscordConstants

async def setup(client:commands.Bot, config):
    await client.add_cog(BaseModule(client, config))

class BaseModule(commands.Cog):
    # TODO: Make class vars and _
    client: commands.Bot | None = None
    bot_started = False # NOTE: Deprecated
    config = None
    version = "Unknown"
    d_consts:DiscordConstants = None
    sql:SQLManager = None


    def __init__(self, client, config=None):
        # Load config 
        if config:
            type(self).config = config

        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.d_consts = self.client.get_cog("DiscordConstants")
        # TODO: Using class variables for some of these things, instance for others

        config = type(self).config
        if config:
            if config["sql_enabled"]:
                print(config["sql_enabled"])
                self.sql = SQLManager()
            self.version = config["version"]
            print(config["version"])


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