from enum import Enum

import discord
from discord import app_commands
from datetime import timedelta

from modules.base import BaseModule

class EmbedType(Enum):
    MOD_MAIL = 0
    USER_MANAGEMENT = 1
    ACTIVITY_LOG = 2
    MISC = 3

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
            case EmbedType.USER_MANAGEMENT:
                embed.set_author(name="User Management",icon_url="https://i.imgur.com/qVFFeRM.png")
            case EmbedType.ACTIVITY_LOG:
                embed.set_author(name="Activity Logs")
            case EmbedType.MISC:
                embed.set_author(name="Miscellaneous")
        
        if self.error:
            embed.title = "<:alert:1346654360012329044> An error occured!"
            embed.color = 0xFF264D
        embed.set_footer(text=f"That Bot v{self.version}")

        return embed



