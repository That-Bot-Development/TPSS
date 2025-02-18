import discord
from discord.ext import commands

from modules.base import BaseModule


class ArtManager(BaseModule):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == self.d_consts.CHANNEL_YOURART and bool(message.embeds):
            # Create thread on new art posts
            await message.channel.create_thread(f"Discussion - {message.author.display_name}'s Art",message=message)
        elif message.channel.id == self.d_consts.CHANNEL_YOURART:
            # Delete non-art messages
            await message.delete()
