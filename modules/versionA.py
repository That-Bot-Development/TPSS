import discord
from discord import app_commands

from modules.base import BaseModule
from modules.util.embed_maker import *

import requests
import time


class Commands(BaseModule):
    asleep = False

    def __init__(self, client):
        self.client = client

    @app_commands.command(name="pet", description="Pet the furret!")
    async def pet(self, interactions: discord.Interaction):
        if not self.asleep:
            await interactions.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.VERSION_A,
                message="",
                title="Furret enjoys being pet! :heart:",
                image_url="https://i.imgur.com/rtUftSV.png"
            ).create())
        else:
            await self.respond_sleeping(interactions)

    @app_commands.command(name="praise", description="Praise furret!")
    async def praise(self, interactions: discord.Interaction):
        if not self.asleep:
            await interactions.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.VERSION_A,
                message="",
                title="Furret blesses you!",
                image_url="https://i.imgur.com/hPhnuXP.png"
            ).create())
        else:
            await self.respond_sleeping(interactions)

    @app_commands.command(name="dance", description="Have furret dance!")
    async def dance(self, interactions: discord.Interaction):
        if not self.asleep:
            await interactions.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.VERSION_A,
                message="",
                title="Furret does a dance!",
                image_url="https://i.imgur.com/qJFoMZP.gif"
            ).create())
        else:
            await self.respond_sleeping(interactions)

    @app_commands.command(name="walk", description="Have furret walk!")
    async def walk(self, interactions: discord.Interaction):
        if not self.asleep:
            await interactions.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.VERSION_A,
                message="",
                title="He walc",
                image_url="https://i.imgur.com/mR65hTH.gif"
            ).create())
        else:
            await self.respond_sleeping(interactions)

    @app_commands.command(name="sleep", description="Have the furret fall asleep!")
    async def sleep(self, interactions: discord.Interaction):
        if not self.asleep:
            await interactions.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.VERSION_A,
                message="",
                title="Furret is feeling sleepy... :zzz:",
                image_url="https://i.imgur.com/ogZ7gf5.png"
            ).create())
            self.asleep = True

        else:
            await interactions.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.VERSION_A,
                message="",
                title="Furret is already sleeping... :zzz:",
                image_url="https://i.imgur.com/ogZ7gf5.png"
            ).create())

    @app_commands.command(name="wake", description="Have the furret fall asleep!")
    async def wake(self, interactions: discord.Interaction):
        if self.asleep:
            await interactions.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.VERSION_A,
                message="",
                title="Furret wakes up!",
                image_url="https://i.imgur.com/OI4XmaQ.gif"
            ).create())
            self.asleep = False
        else:
            await interactions.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.VERSION_A,
                message="",
                title="Furret is already awake!",
                image_url="https://i.imgur.com/OI4XmaQ.gif"
            ).create())
        asleep = False

    async def respond_sleeping(self, interactions:discord.Interaction):
        await interactions.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.VERSION_A,
                message="-# `/wake` to awaken",
                title="Furret is sleeping! :zzz:",
                image_url="https://i.imgur.com/ogZ7gf5.png"
        ).create())

    