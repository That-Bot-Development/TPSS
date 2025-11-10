import discord
from discord.ext import commands
from datetime import datetime as DT

from modules.base import BaseModule

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
                embed = discord.Embed(title="#general Name Change!", 
                                      description=f"Name Changed to ***#{after.name}***", 
                                      timestamp=DT.now(), 
                                      color=discord.Color.random(seed=int(DT.now().timestamp())))
                embed.set_footer(text="That Bot vUnknown") #Theres probaly a way to get the version, but i dont wanna figure that out, used modmail as reference.
                await self.d_consts.CHANNEL_GENERAL_HISTORY.send(embed=embed)

