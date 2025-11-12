from enum import Enum

import discord
from discord.ext import commands

from bot_client import Client

class EmbedType(Enum):
    MOD_MAIL = 0
    USER_MANAGEMENT = 1
    ACTIVITY_LOG = 2
    MISC = 3

class EmbedMaker(): # This probably should not extend BaseModule 
    def __init__(self, client:Client):
        self.client = client

    def create(self, embed_type:EmbedType, message:str, title:str="", image_url:str="", color:discord.Colour|int=0x69b2ff, error:bool=False):
        embed = discord.Embed(color=self.color, title=self.title,description=self.message)

        if self.image_url is not None:
            embed.set_image(url=self.image_url)

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
        embed.set_footer(text=f"That Bot v{self.client.version}")

        return embed



