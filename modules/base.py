import discord
from discord.ext import commands;

from modules.util.sql_manager import SQLManager


class BaseModule(commands.Cog):
    # "Global" items that all modules should be able to access
    bot_started = False
    version = "2.7.0" # Move to config, add getter

    d_consts = None
    sql:SQLManager = None

    async def get_member(self, user_id) -> discord.Member: # TODO: Should this even be here?
        server:discord.Guild = self.d_consts.SERVER
        try:
            return server.get_member(user_id) or await server.fetch_member(user_id)
        except Exception:
            return None

