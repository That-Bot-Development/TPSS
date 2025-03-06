import discord
from discord import app_commands

from modules.base import BaseModule
from modules.util.embed_maker import *


class SQLQuery(BaseModule):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="query", description="[Admin] Run a QUERY operation on the database.")
    @app_commands.describe(query="Your query.")
    async def query(self, interactions: discord.Interaction, query:str):
        if not self.d_consts.ROLE_ADMIN in interactions.user.roles:
            return
        
        try:
            result = self.sql.execute_query(query=query)
        except Exception as e:
            print(f"Exception occured in 'query' operation: {e}")
            await interactions.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.MISC,
                message=str(e),
                error=True
            ).create(),ephemeral=True,delete_after=20)
            return

        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.MISC,
            title="Query Result",
            message=result
        ))

        