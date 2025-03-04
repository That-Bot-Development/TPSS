import discord
from discord import app_commands

from modules.base import BaseModule
from modules.util.embed_maker import *

import mysql.connector as my_sql


class SQLQuery(BaseModule):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="query", description="[Admin] Run a QUERY operation on the database.")
    @app_commands.describe(query="Your query.")
    async def query(self, interactions: discord.Interaction, query:str):
        if not self.d_consts.ROLE_ADMIN in interactions.user.roles:
            await interactions.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.MISC,
                message=f"Access is restricted.",
                error=True
            ).create(),ephemeral=True,delete_after=20)
            return
        
        try:
            result = self.sql.execute_query(query=query,handle_except=False)
        except Exception as e:
            print(f"Exception occured in 'query' operation: {e}")
            await interactions.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.MISC,
                message=f"```{e}```",
                error=True
            ).create())
            return

        if result:
            result_f = ""
            for row in result:
                # For each row, join its values with spaces or another separator
                result_f += "\n".join(f"{key}: {value}" for key, value in row.items())
                result_f += "\n\n"  # Add space between rows for readability
        else:
            result_f = "Changes Applied"

        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.MISC,
            title="Query Result",
            message=f"```{result_f}```"
        ).create())

        