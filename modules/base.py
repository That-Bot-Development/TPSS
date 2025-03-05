from discord.ext import commands;

from modules.util.sql_manager import SQLManager


class BaseModule(commands.Cog):
    # "Global" items that all modules should be able to access
    xz = None
    bot_started = False
    version = "2.7.0"