import discord
from discord.ext import commands
from discord.ui import Select, Button, View
from discord import app_commands

from modules.base import BaseModule
from modules.modmail.ticket_types import ReportMember, StateQuestionConcern, SuggestPoll, ReportMod, ReportEventManager, Other
from modules.util.embed_maker import *


class ModMail(BaseModule):
    def __init__(self, client):
        self.client = client

    async def start_persistent_interactions(self):
        '''Function to start all interactions that should resume function on startup.'''
        await self.ticket_creator()

    async def get_ticket(self, creator):
        '''Function to get ticket by ticket creator. There should only be one ticket per person up at any given time.'''
        # NOTE: This prevents staff from making tickets. Moving this to a ticket ID system instead will fix this
        for thread in self.d_consts.CHANNEL_MODMAIL.threads:
            if thread.owner == self.client.user and thread.archived is False:
                for member in await thread.fetch_members():
                    if member.id == creator.id:
                        return thread
        return None

    async def create_ticket(self, interaction:discord.Interaction,tt_data):
        active_ticket = await self.get_ticket(interaction.user)
        if active_ticket is None:
            tt_ticket_data = tt_data["ticketdata"]

            new_ticket = await self.d_consts.CHANNEL_MODMAIL.create_thread(name=interaction.user.display_name,reason=f"Mod Mail ticket created by {interaction.user.display_name}")
            await new_ticket.edit(invitable=False)
            msg:discord.Message = await new_ticket.send(f"<@&{tt_ticket_data[0]}> {self.d_consts.ROLE_COREBOTS.mention} {interaction.user.mention}")
            if tt_ticket_data[0] != self.d_consts.ROLE_ADMIN.id:
                await msg.edit(content=f"{self.d_consts.ROLE_MOD.mention} {self.d_consts.ROLE_ADMIN.mention} {self.d_consts.ROLE_OWNER.mention}")
            await msg.edit(content="",embed=EmbedMaker(
                embed_type=EmbedType.MOD_MAIL,
                title=f"{str(tt_ticket_data[1]).title()} Ticket",
                message=f"New {tt_ticket_data[1]} ticket from **{interaction.user.display_name}**.\n\n-# Staff can close the ticket with `/close`."
            ).create())

            await interaction.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.MOD_MAIL,
                title="Ticket Created",
                message=f"Your {tt_ticket_data[1]} ticket has been created! You can find it and send your {tt_ticket_data[1]} here: <#{new_ticket.id}>"
            ).create(),ephemeral=True,delete_after=120)
        else:
            await interaction.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.MOD_MAIL,
                message=f"You already have an active ticket! You can find it here: <#{active_ticket.id}>",
                error=True
            ).create(),ephemeral=True,delete_after=120)

    async def get_ticket_type_data(self, select):
        '''Function to get data for the ticket type selection.'''
        match select.values[0]:
            case "Report a Member":
                data = [ReportMember.SELECT_DATA,ReportMember.TICKET_DATA]
            case "State a Question or Concern":
                data = [StateQuestionConcern.SELECT_DATA,StateQuestionConcern.TICKET_DATA]
            case "Suggest a Poll":
                data = [SuggestPoll.SELECT_DATA,SuggestPoll.TICKET_DATA]
            case "Report a Mod":
                data = [ReportMod.SELECT_DATA,ReportMod.TICKET_DATA]
            case "Report an Event Manager":
                data = [ReportEventManager.SELECT_DATA,ReportEventManager.TICKET_DATA]
            case "Other":
                data = [Other.SELECT_DATA,Other.TICKET_DATA]
        return {"selectdata":data[0],"ticketdata":data[1]}

    async def ticket_creator(self):
        mm_select = Select(
            placeholder="Create new ticket",
            options=[
                discord.SelectOption(
                    label=ReportMember.SELECT_DATA[0],
                    emoji=ReportMember.SELECT_DATA[1],
                    description=ReportMember.SELECT_DATA[2]),
                discord.SelectOption(
                    label=StateQuestionConcern.SELECT_DATA[0],
                    emoji=StateQuestionConcern.SELECT_DATA[1],
                    description=StateQuestionConcern.SELECT_DATA[2]),
                discord.SelectOption(
                    label=SuggestPoll.SELECT_DATA[0],
                    emoji=SuggestPoll.SELECT_DATA[1],
                    description=SuggestPoll.SELECT_DATA[2]),
                discord.SelectOption(
                    label=ReportMod.SELECT_DATA[0],
                    emoji=ReportMod.SELECT_DATA[1],
                    description=ReportMod.SELECT_DATA[2]),
                discord.SelectOption(
                    label=ReportEventManager.SELECT_DATA[0],
                    emoji=ReportEventManager.SELECT_DATA[1],
                    description=ReportEventManager.SELECT_DATA[2]),
                discord.SelectOption(
                    label=Other.SELECT_DATA[0],
                    emoji=Other.SELECT_DATA[1],
                    description=Other.SELECT_DATA[2]),
            ]
        )

        async def callback(interaction):
            tt_data = await self.get_ticket_type_data(mm_select)
            await self.create_ticket(interaction,tt_data)

        mm_select.callback = callback

        view = View(timeout=None)
        view.add_item(mm_select)

        msg = await self.d_consts.CHANNEL_MODMAIL.fetch_message(1040873181159886909) #TODO: Move reference to config whenever that is done
        await msg.edit(content="", embed=EmbedMaker(
            embed_type=EmbedType.MOD_MAIL,
            title="That Place Mod Mail",
            message="**Use the dropdown below to create a modmail ticket.**\nOnce you select an option, a thread will be created where you can speak with the staff team directly.\n\n*Any non-serious tickets must be submitted as 'Other'.*"
        ).create(),view=view)

    @app_commands.command(name="close", description="Closes the mod mail ticket that the command is sent in.")
    async def close(self, interactions: discord.Interaction):
        if interactions.channel in self.d_consts.CHANNEL_MODMAIL.threads:
            await interactions.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.MOD_MAIL,
                title="Ticket Closed",
                message=f"Closed by {interactions.user.display_name}."
            ).create())
            await self.d_consts.CHANNEL_MISCLOGS.send(embed=EmbedMaker(
                embed_type=EmbedType.MOD_MAIL,
                title="Ticket Closed",
                message=f"{interactions.channel.mention}"
            ).create())
            await interactions.channel.edit(archived=True,locked=True)

    @commands.Cog.listener()
    async def on_ready(self):
        # This should only ron on initial boot
        if self.bot_started is False:
            # Generate persistent interactions
            await self.start_persistent_interactions()
