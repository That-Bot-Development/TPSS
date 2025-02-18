import discord
from discord.ext import commands

from modules.base import BaseModule


class ArtManager(BaseModule):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel == self.d_consts.CHANNEL_YOURART:
            # Check if message contains URL
            has_url = False
            for word in message.content.split():
                if 'https://' in word or 'http://' in word:
                    has_url = True
            # Check if message contains attachments
            if len(message.attachments) > 0 or has_url == True:
                # Create thread on new art posts
                await message.create_thread(name=f"Discussion - {message.author.display_name}'s Art")
                print("Image")
                
            else:
                await message.delete()
            print(f"{has_url} and {len(message.attachments) > 0}")