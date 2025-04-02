import discord
from discord import app_commands

from modules.base import BaseModule
from modules.util.embed_maker import *

import requests
import time
import random


class Say(BaseModule):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="say", description="Attempt to get That Furret to respond.")
    @app_commands.describe(message="The message to have the furret say.",replyto="The Message ID of the message the furret will respond to.")
    async def say(self, interactions: discord.Interaction, message:str, replyto:str=None):

        try:
            if self.d_consts.ROLE_OWNER in interactions.user.roles or self.d_consts.ROLE_ADMIN in interactions.user.roles or self.d_consts.ROLE_MOD in interactions.user.roles:
                if replyto == None:
                    response = await interactions.channel.send(message)
                else:
                    response = await interactions.channel.fetch_message(replyto)
                    await response.reply(message)
                await self.d_consts.CHANNEL_MISCLOGS.send(embed=EmbedMaker(
                    embed_type=EmbedType.ACTIVITY_LOG,
                    title = "Say Command",
                    message=f"**{interactions.user.display_name}:** {message} ({response.jump_url})"
                ).create(),silent=True,allowed_mentions=self.d_consts.VAR_ALLOWEDMENTIONS_NONE)
                await interactions.response.send_message("<:Advertisement:622603404212174849>",ephemeral=True,delete_after=0)
            else:
                messages = [
                    f"Who do you think you are to command me around, {interactions.user.mention}?",
                    f"Who even are you, {interactions.user.mention}?",
                    f"Furret doesn't take commands from strangers, {interactions.user.mention}.",
                    f"Who do you think you are, {interactions.user.mention}?",
                    f"{interactions.user.mention}...",
                    f"I've had enough, {interactions.user.mention}."
                ]
                await interactions.response.send_message(content=messages[random.randint(0,5)])

        except Exception as e:
            print(f"Exception occured in 'say' operation: {e}")
            await interactions.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.MISC,
                message="This likely means That Bot does not have access to speak in this channel.\n\nContact an Admin if you believe this is a mistake.",
                error=True
            ).create(),ephemeral=True,delete_after=20)
class Cat(BaseModule):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="cat", description="Provides cat.")
    @app_commands.describe(filter="Filter what type of cat you would like provided.")
    async def cat(self, interactions: discord.Interaction, filter:str=None):

        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.MISC,
            message="A cat is not a furret.\nWhy would you use this command?",
            error=True
        ).create())

