import discord
from discord.ext import commands
from discord import app_commands

from modules.base import BaseModule
from modules.modmail.mod_mail import ModMail
from modules.modmail.ticket_types import ReportMember
from modules.util.embed_maker import *


class ReportMessage(BaseModule):
    def __init__(self, client):
        super().__init__(client)
        self.mod_mail = None

    @commands.Cog.listener()
    async def on_ready(self):
        cog = self.client.get_cog("ModMail")
        if isinstance(cog, ModMail):
            self.mod_mail: ModMail = cog

    @app_commands.context_menu(name="Report Message")
    async def report_message(self, interaction: discord.Interaction, message: discord.Message):
        """Report a message via modmail."""
        
        # Prevent reporting outside of guild or self
        if message.guild is None or message.author.id == interaction.user.id:
            return await interaction.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.MOD_MAIL,
                message="You cannot report yourself!",
                error=True
            ).create(), ephemeral=True, delete_after=20)

        # Use the ReportMember ticket type
        await self.create_ticket(
            interaction,
            ReportMember.TICKET_DATA,
            reported_message=message
        )