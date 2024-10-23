import discord
from discord import app_commands

from modules.base import BaseModule

import requests
import time


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

    @app_commands.command(name="cat", description="Provides cat.")
    @app_commands.describe(filter="Filter what type of cat you would like provided.")
    async def cat(self, interactions: discord.Interaction, filter:str=None):

        try:
            if filter == None:
                response = requests.get(f"https://cataas.com/cat?{int(time.time())}")
            else:
                response = requests.get(f"https://cataas.com/cat/{filter}?{int(time.time())}")
            if response.status_code == 200:
                # Create a Discord embed with the cat image
                embed = discord.Embed(title="")
                embed.set_image(url=response.url)  # Use the URL from the response
                await interactions.response.send_message(embed=embed)
            else:
                print(response.status_code)

        except Exception as e:
            print(f"Exception occured in 'cat' operation: {e}")
            await interactions.response.send_message("**An error occured!**\nThis likely means the [CatAAS API](https://cataas.com/) is down.\nContact an Admin if you believe this is a mistake.",ephemeral=True,delete_after=10)
        
