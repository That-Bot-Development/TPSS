import discord
from discord import app_commands

from modules.base import BaseModule

import aiohttp
import asyncio
from io import BytesIO


class Say(BaseModule):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="say", description="Put words in That Bot's figurative mouth.")
    @app_commands.describe(message="The message to have the bot send.",replyto="The Message ID of the message the bot will respond to.")
    async def say(self, interactions: discord.Interaction, message:str, replyto:str=None):

        try:
            if replyto == None:
                response = await interactions.channel.send(message)
            else:
                response = await interactions.channel.fetch_message(replyto)
                await response.reply(message)
            await self.d_consts.CHANNEL_MISCLOGS.send(f"> **/say from {interactions.user.display_name}:** {message} ({response.jump_url})",silent=True,allowed_mentions=self.d_consts.VAR_ALLOWEDMENTIONS_NONE)
            await interactions.response.send_message("<:Advertisement:622603404212174849>",ephemeral=True,delete_after=0)

        except Exception as e:
            print(f"Exception occured in 'say' operation: {e}")
            await interactions.response.send_message("**An error occured!**\nThis likely means That Bot does not have access to speak in this channel.\nContact an Admin if you believe this is a mistake.",ephemeral=True,delete_after=10)

class Cat(BaseModule):
    def __init__(self, client):
        self.client = client
    
    async def fetch(self, session, url, method='GET', params=None, headers=None):
        try:
            async with session.request(method, url, headers=headers, params=params, json=None) as response:
                response.raise_for_status()
                content_type = response.headers.get('Content-Type', '')

                # Check if the response is an image
                if content_type.startswith('image/'):
                    return await response.read(), content_type.split('/')[-1]  # Return bytes and file extension
                else:
                    print("Response is not an image.")
                    return None, None
        except aiohttp.ClientError as e:
            print(f"HTTP error occurred: {e}")
            return None

    @app_commands.command(name="cat", description="Provides cat.")
    @app_commands.describe(filter="Filter what type of cat you would like provided.")
    async def cat(self, interactions: discord.Interaction, filter:str=None):

        #try:
        cat = None
        async with aiohttp.ClientSession() as s:
            cat, file_ext = await self.fetch(s,f"https://cataas.com/cat/{filter}",headers={'accept':'image/*'})
        file = discord.File(BytesIO(cat), filename=f"cat.{file_ext}")
        print("bro " + file_ext)
        await interactions.response.send_message(file=file)

        #except Exception as e:
         #   print(f"Exception occured in 'cat' operation: {e}")
         #   await interactions.response.send_message("**An error occured!**\nThis likely means the [CatAAS API](https://cataas.com/) is down.\nContact an Admin if you believe this is a mistake.",ephemeral=True,delete_after=10)
        
