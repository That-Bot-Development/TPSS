import discord
from discord import app_commands

from modules.base import BaseModule


class Utilities(BaseModule):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="query", description="[Admin] Run a QUERY operation on the database.")
    @app_commands.describe(query="Your query.")
    async def query(self, interactions: discord.Interaction, query:str):
        self.sql.execute_query(query=query)