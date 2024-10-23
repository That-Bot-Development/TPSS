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


# Set up bot
TOKEN = "NjA1NDk1NTMwMTM4NzYzMjg3.GwyTQb.ud3w88CLyX1SpYEoJEim-eZNukycfor1j2VEco" # IDK WHY THIS IS STILL HERE
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


# Initialize cogs
async def init_cogs():
    # Instantiate singleton utilities & initialize reference vars
    await client.add_cog(d_consts.DiscordConstants(client))
    base.BaseModule.d_consts = d_consts.DiscordConstants.get()

    # Initialize modules
    await client.add_cog(mm.ModMail(client))
    await client.add_cog(bd.BanDM(client))
    await client.add_cog(sm.SuggestionManager(client))
    await client.add_cog(f.Say(client))
    await client.add_cog(f.Cat(client))

asyncio.run(init_cogs())

# Run bot
client.run(TOKEN)


#FIX #
##async def on_ready():
    ##base.BaseModule.bot_started = True``
    ##print("Bot active!")

# Ensure cogs are loaded before calling main on_ready listener
##@client.before_invoke
##async def wait_for_cogs():
    ##await client.wait_until_ready()