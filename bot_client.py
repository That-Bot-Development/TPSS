import discord
from discord.ext import commands

from modules.util.sql_manager import SQLManager
from modules.util.embed_maker import EmbedMaker

from modules.util.discord_const import DiscordConstants

from typing import Any

class Client(commands.Bot):
    sql: SQLManager | None = None
    embeds: EmbedMaker | None = None
    config: dict[str, Any] | None = None
    version: str = "Unknown"
    guild: discord.Guild | None = None
    d_consts: DiscordConstants | None = None


    def __init__(self, *, intents: discord.Intents, config: dict[str, Any]):
        self.config = config

        super().__init__(intents=intents, command_prefix="db_tpss!")
        print("[Setup] Bot client initialized.")

    async def setup_hook(self):
        if self.config:
            if self.config["sql_enabled"]:
                self.sql = SQLManager()
            self.version = self.config["version"]
            self.guild = self.config["guild"]

        self.embeds = EmbedMaker(self)
        
        if self.guild: # single-server
            self.tree.copy_global_to(guild=self.guild)
            await self.tree.sync(guild=self.guild)