import discord
from discord.ext import commands

from modules.base import BaseModule

from bot_client import Client

async def setup(client:Client, config):
    await client.add_cog(ArtManager(client))

class ArtManager(BaseModule):
    def __init__(self, client: Client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel == self.client.d_consts.CHANNEL_YOURART:
            # Check if message contains URL
            has_url = False
            for word in message.content.split():
                if 'https://' in word or 'http://' in word:
                    has_url = True
            # Check if message contains attachments
            if len(message.attachments) > 0 or has_url == True:
                # Create thread on new art posts
                await message.create_thread(name=f"Discussion - {message.author.display_name}'s Art")
            else:
                await message.delete()