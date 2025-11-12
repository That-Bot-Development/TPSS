import discord
from discord.ext import commands
from datetime import datetime as DT

from modules.base import BaseModule
from util.embed_maker import *

async def setup(client:commands.Bot, config):
    await client.add_cog(GeneralManager(client))

class GeneralManager(BaseModule):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        if after == self.d_consts.CHANNEL_GENERAL:
            await self.d_consts.CHANNEL_GENERAL.edit(slowmode_delay=3)
            if after.name != before.name:
                await self.d_consts.CHANNEL_GENERAL_HISTORY.send(embed=self.client.embeds.create(
                    embed_type=EmbedType.ACTIVITY_LOG,
                    title = "#general Name Change!",
                    message=f"Name Changed to ***#{after.name}***",
                    color=discord.Colour.random(seed=int(DT.now().timestamp()))))

