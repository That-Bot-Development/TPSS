import discord
from discord.ext import commands

import asyncio
import importlib as imp
import tomllib

from bot_client import Client
import modules.util.sql_manager as sql
import modules.util.embed_maker as embed

intents = discord.Intents.all() 

# Load configuration

with open("config.toml", "rb") as f:
    CONFIG = tomllib.load(f)

DEBUG_MODE:bool = CONFIG["debug_mode"]

MODULES: list[str] = CONFIG["debug_modules" if DEBUG_MODE else "modules"]

GUILD: discord.Object = CONFIG["guild"]


# Initialize client
client = Client(intents=intents,config=CONFIG)

async def getToken():
     with open('private/token.txt', 'r') as file:
        token = file.readline()
        return token

async def init_modules():
    for module_path in MODULES:
        try:
            module = imp.import_module(module_path)

            if hasattr(module, "setup"):
                await module.setup(client, CONFIG)
                print(f"[Setup] Successfully loaded {module_path}.")
            else:
                raise Exception("No setup function found!")
        except Exception as e:
            print(f"[Setup] Failed to load {module_path}: {e}")

    await initialize_cog_global_resources()


async def initialize_cog_global_resources():
    client.d_consts = client.get_cog("DiscordConstants")


# Initialize cogs
asyncio.run(init_modules())

# Run bot
client.run(asyncio.run(getToken()))