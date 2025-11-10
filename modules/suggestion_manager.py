import discord
from discord.ext import commands

from bot_client import Client
from modules.base import BaseModule

async def setup(client:Client, config):
    await client.add_cog(SuggestionManager(client))

class SuggestionManager(BaseModule):
    def __init__(self, client: Client):
        self.client = client

    @commands.Cog.listener()
    async def on_thread_create(self, thread):
        if thread.parent == self.client.d_consts.CHANNEL_SUGGESTIONS:
            base_msg = await thread.fetch_message(thread.id)
            await base_msg.add_reaction("👍")
            await base_msg.add_reaction("👎")

            ping_msg = await thread.send(f"{self.client.d_consts.ROLE_COREBOTS.mention}")
            await ping_msg.delete()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel == self.client.d_consts.CHANNEL_EMOTE_SUGGESTIONS and message.author != self.client.user:
            if message.attachments != []:
                await message.add_reaction("👍")
                await message.add_reaction("👎")
                
                if 'sticker' not in str(message.content).lower() and 'emoji' not in str(message.content).lower():
                    await message.reply(content='Please make sure you have a [STICKER] or [EMOTE] idenifier attached to your message.', delete_after=3)
            else:
                await message.delete()
