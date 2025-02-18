import discord
import asyncio

import util.discord_const as d_consts
from discord import app_commands
from discord.ext import commands

import modules.base as base
import modules.mod_mail as mm
import modules.ban_dm as bd
import modules.fun as f
import modules.suggestion_manager as sm
import modules.art_manager as am


# Set up bot
GUID = discord.Object(id=578356230637223936)
intents = discord.Intents.all() 

class aClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents,command_prefix="db_tpss!")
        print("Started up!")
    async def setup_hook(self):
        self.tree.copy_global_to(guild=GUID)
        await self.tree.sync(guild=GUID)

client = aClient(intents=intents)


async def getToken():
     with open('private/token.txt', 'r') as file:
        token = file.read()
        return token

# Initialize cogs
async def init_cogs():
    # Instantiate singleton utilities & initialize reference vars
    await client.add_cog(d_consts.DiscordConstants(client))
    base.BaseModule.d_consts = d_consts.DiscordConstants.get()

    # Initialize modules
    await client.add_cog(mm.ModMail(client))
    await client.add_cog(bd.BanDM(client))
    await client.add_cog(sm.SuggestionManager(client))
    await client.add_cog(am.ArtManager(client))
    await client.add_cog(f.Say(client))
    await client.add_cog(f.Cat(client))

# Initialize cogs
asyncio.run(init_cogs())

# Run bot
client.run(asyncio.run(getToken()))

#FIX #
##async def on_ready():
    ##base.BaseModule.bot_started = True``
    ##print("Bot active!")

# Ensure cogs are loaded before calling main on_ready listener
##@client.before_invoke
##async def wait_for_cogs():
    ##await client.wait_until_ready()