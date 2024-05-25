from discord.ext import commands;


class BaseModule(commands.Cog):
    # "Global" items that all modules should be able to access
    d_consts = None
    bot_started = False
