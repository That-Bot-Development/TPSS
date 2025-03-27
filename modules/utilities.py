import discord
from discord import app_commands
from discord.ui import View, Button

from modules.base import BaseModule
from modules.util.embed_maker import *

class SQLQuery(BaseModule):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="query", description="[Admin] Run a SQL query on the database.")
    @app_commands.describe(query="Your query.")
    async def query(self, interaction: discord.Interaction, query: str):
        if not self.d_consts.ROLE_ADMIN in interaction.user.roles:
            await interaction.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.MISC,
                message=f"Access is restricted.",
                error=True
            ).create(), ephemeral=True, delete_after=20)
            return
        
        # Send initial response to prevent timeout
        await interaction.response.defer()
        
        try:
            result = self.sql.execute_query(query=query, handle_except=False)
        except Exception as e:
            print(f"Exception occurred in 'query' operation: {e}")
            await interaction.followup.send(embed=EmbedMaker(
                embed_type=EmbedType.MISC,
                message=f"```{e}```",
                error=True
            ).create())
            return

        if not result:
            await interaction.followup.send(embed=EmbedMaker(
                embed_type=EmbedType.MISC,
                title="Query Result",
                message="No result returned"
            ).create())
            return

        pages = [""]
        for row in result:
            entry = "\n".join(f"{key}: {value}" for key, value in row.items()) + "\n\n"
            if len(pages[-1]) + len(entry) > 1900:
                pages.append("")
            pages[-1] += entry
        
        class PaginationView(View):
            def __init__(self, pages):
                super().__init__()
                self.pages = pages
                self.current_page = 0
                self.update_buttons()

            async def update_message(self, interaction: discord.Interaction):
                self.update_buttons()
                await interaction.response.edit_message(embed=EmbedMaker(
                    embed_type=EmbedType.MISC,
                    title=f"Query Result (Page {self.current_page + 1}/{len(self.pages)})",
                    message=f"```{self.pages[self.current_page]}```"
                ).create(), view=self)

            def update_buttons(self):
                self.children[0].disabled = (self.current_page == 0)
                self.children[1].disabled = (self.current_page == 0)
                self.children[2].disabled = (self.current_page == int(len(self.pages)/2))
                self.children[3].disabled = (self.current_page == len(self.pages) - 1)
                self.children[4].disabled = (self.current_page == len(self.pages) - 1)

            @discord.ui.button(label="⏪", style=discord.ButtonStyle.grey)
            async def first(self, interaction: discord.Interaction, button: Button):
                self.current_page = 0
                await self.update_message(interaction)

            @discord.ui.button(label="◀️", style=discord.ButtonStyle.grey)
            async def previous(self, interaction: discord.Interaction, button: Button):
                self.current_page -= 1
                await self.update_message(interaction)

            @discord.ui.button(label="⏺️", style=discord.ButtonStyle.grey)
            async def middle(self, interaction: discord.Interaction, button: Button):
                self.current_page = int(len(self.pages)/2)
                await self.update_message(interaction)

            @discord.ui.button(label="▶️", style=discord.ButtonStyle.grey)
            async def next(self, interaction: discord.Interaction, button: Button):
                self.current_page += 1
                await self.update_message(interaction)

            @discord.ui.button(label="⏩", style=discord.ButtonStyle.grey)
            async def last(self, interaction: discord.Interaction, button: Button):
                self.current_page = len(self.pages) - 1
                await self.update_message(interaction)

        
        view = PaginationView(pages) if len(pages) > 1 else discord.utils.MISSING
        await interaction.followup.send(embed=EmbedMaker(
            embed_type=EmbedType.MISC,
            title=f"Query Result (Page 1/{len(pages)})",
            message=f"```{pages[0]}```"
        ).create(), view=view)
