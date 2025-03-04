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
    MISC = 4

class EmbedMaker(BaseModule):
    def __init__(self, embed_type:EmbedType, message:str, title:str="", error:bool=False):
        #self.client = client
        self.embed_type = embed_type
        self.message = message
        self.title = title
        self.error = error

    def create(self):
        embed = discord.Embed(color=0x69B2FF, title=self.title,description=self.message)

        match self.embed_type:
            case EmbedType.MOD_MAIL:
                embed.set_author(name="Mod Mail",icon_url="https://i.imgur.com/qY9GMcV.png")
            case EmbedType.PUNISHMENT_CMD:
                embed.set_author(name="User Management",icon_url="https://i.imgur.com/qVFFeRM.png")
            case EmbedType.PUNISHMENT_LOG:
                embed.set_author(name="Punishment Logs")
            case EmbedType.ACTIVITY_LOG:
                embed.set_author(name="Activity Logs")
            case EmbedType.MISC:
                embed.set_author(name="Miscellaneous")
        
        if self.error:
            embed.title = "\⚠️ An error occured!"
            embed.color = 0xFF264D
        embed.set_footer(text=f"That Bot v{self.version}")

        return embed



