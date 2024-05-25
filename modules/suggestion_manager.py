import discord
from discord.ext import commands

from modules.base import BaseModule


class SuggestionManager(BaseModule):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_thread_create(self, thread):
        if thread.parent == self.d_consts.CHANNEL_SUGGESTIONS:
            base_msg = await thread.fetch_message(thread.id)
            await base_msg.add_reaction("👍")
            await base_msg.add_reaction("👎")

            ping_msg = await thread.send(f"{self.d_consts.ROLE_COREBOTS.mention}")
            await ping_msg.delete()
