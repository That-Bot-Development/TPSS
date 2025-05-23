import discord
from discord.ext import commands
from discord import app_commands

from modules.modmail.mod_mail import ModMail
from modules.modmail.ticket_types import ReportMember
from modules.util.embed_maker import *

mod_mail: ModMail | None = None

async def setup(client: commands.Bot):
    global mod_mail

    client.tree.add_command(report_message)

    @client.event
    async def on_ready():
        global mod_mail

        cog = client.get_cog("ModMail")
        if isinstance(cog, ModMail):
            mod_mail = cog

@app_commands.context_menu(name="Report Message")
async def report_message(interaction: discord.Interaction, message: discord.Message):
    """Report a message via modmail."""
    
    # Prevent reporting outside of guild or self
    if message.guild is None or message.author.id == interaction.user.id:
        return await interaction.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.MOD_MAIL,
            message="You cannot report yourself!",
            error=True
        ).create(), ephemeral=True, delete_after=20)

    # Use the ReportMember ticket type
    await mod_mail.create_ticket(
        interaction,
        ReportMember.TICKET_DATA,
        reported_message=message
    )