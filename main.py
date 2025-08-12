import discord
from discord.ext import commands

import asyncio
import importlib as imp
import tomllib


GUID = discord.Object(id=578356230637223936)
intents = discord.Intents.all() 


# Load configuration

with open("config.toml", "rb") as f:
    CONFIG = tomllib.load(f)

DEBUG_MODE:bool = CONFIG["debug_mode"]

MODULES: list[str] = CONFIG["debug_modules" if DEBUG_MODE else "modules"]

GUILD: discord.Object = CONFIG["guild"]


# Initialize client

class aClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents,command_prefix="db_tpss!")
        print("[Setup] Bot client initialized.")
    async def setup_hook(self): # single-server
        self.tree.copy_global_to(guild=GUID)
        await self.tree.sync(guild=GUID)

client = aClient(intents=intents)


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


# Initialize cogs
asyncio.run(init_modules())

# Run bot
client.run(asyncio.run(getToken()))