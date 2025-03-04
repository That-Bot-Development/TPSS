from enum import Enum

import discord
from discord import app_commands
from datetime import timedelta

from modules.base import BaseModule

class EmbedType(Enum):
    MOD_MAIL = 0
    PUNISHMENT_CMD = 1
    PUNISHMENT_LOG = 2
    ACTIVITY_LOG = 3

class EmbedMaker(BaseModule):
    def __init__(self, embed_type:EmbedType, message:str, title):
        #self.client = client
        self.embed_type = embed_type
        self.message = message
        self.title = title

    async def create(self):
        embed = discord.Embed(color=0x69B2FF, title=self.title,description=self.message)

        match self.embed_type:
            case EmbedType.MOD_MAIL:
                embed.set_author("Mod Mail")
            case EmbedType.PUNISHMENT_CMD:
                embed.set_author("User Management")
            case EmbedType.PUNISHMENT_LOG:
                embed.set_author("Punishment Logs")
            case EmbedType.ACTIVITY_LOG:
                embed.set_author("Activity Logs")
        
        if self.title == "err":
            embed.title = "An error occured!"
            embed.color = 0xFF264D

        return embed



