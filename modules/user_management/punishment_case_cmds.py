import discord
from discord import app_commands
from discord.ext import commands

from modules.user_management.punishment_system import PunishmentSystem
from modules.user_management.staff_notes import StaffNotes
from modules.util.embed_maker import *
from modules.util.exceptions import NotFoundError

import traceback
from datetime import *


class PunishmentCaseCommands(PunishmentSystem):
    def __init__(self, client):
        self.client = client #TODO this is redundant, done in base class... use super().__init__(client)
        self.staff_notes = None

    @commands.Cog.listener()
    async def on_ready(self):
        cog = self.client.get_cog("StaffNotes")
        if isinstance(cog, StaffNotes):
            self.staff_notes: StaffNotes = cog


    @app_commands.command(name="punishments", description="Lists all punishment cases for the specified user.")
    @app_commands.describe(user="The user to check punishments on.")
    async def punishments(self, interactions: discord.Interaction, user:discord.User=None):
        if user is None:
            user = interactions.user

        message = ""

        try:
            with self.sql.get_connection() as connection:
                #TODO: Re-evaluate if I need to be creating an independent connection when I am only executing one query in the function
                results = self.sql.execute_query("SELECT * FROM Punishments WHERE UserID = %s",(user.id,),connection=connection,handle_except=False)

                if results:
                    lines = []
                    for row in results:
                        date = datetime.strptime(str(row['IssuedAt']),"%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                        lines.append(f"**Case #{row['CaseNo']}** - {row['Type']}\n{row['Reason']}\n-# {date}")
                    message = "\n\n".join(lines)
                else:
                    message = "*No cases found.*"
        except Exception as e:
            await self.create_punishment_err(interactions,"list punishments",e)
            return
        
        if any(role.name == "Staff" for role in interactions.user.roles) and interactions.channel.id == 578725402638286879:

            try:
                notes = self.staff_notes.get_notes(user.id)
                message += f"\n\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n<:note:1374949963825680484> **Notes**\n\n{notes}" if notes else "\n\n<:note:1374949963825680484> *No notes found.*"
            except Exception as e:
                print(f"Exception occured in 'list notes (external)' operation: {e}")

                message += "\n\n-# <:alert:1346654360012329044> Notes could not be loaded."

        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.USER_MANAGEMENT,
            title=f"Punishments: {self.truncate_string(user.display_name)}",
            message=message
        ).create())

    @app_commands.command(name="case", description="View a specific punishment case.")
    @app_commands.checks.has_role("Staff")
    @app_commands.describe(case="The case number.")
    async def case(self, interactions: discord.Interaction, case:app_commands.Range[int, 1, 999999]):        
        try:
            with self.sql.get_connection() as connection:
                results = self.sql.execute_query("SELECT * FROM Punishments WHERE CaseNo = %s",(case,),connection=connection,handle_except=False)

            if results:
                # Sub-header
                user = await self.client.fetch_user(results[0]['UserID'])
                if user is not None:
                    subheader = f"**{user.display_name}** ({user.id})"
                else:
                    subheader = f"**Unknown** ({results[0]['UserID']})"
                subheader += f" - {results[0]['Type']}"

                # Expiry
                expires_on = results[0]['ExpiresAt']
                if expires_on is not None:
                    expiry = f"`{datetime.strptime(str(results[0]['ExpiresAt']),"%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y @ %H:%M:%S")}`"
                else:
                    expiry = "Never"

                # Details on issuance of punishment
                issued_by =  await self.client.fetch_user(results[0]['IssuedByID'])
                issued_details = f"-# Issued {datetime.strptime(str(results[0]['IssuedAt']),"%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")} by "
                if issued_by is not None:
                    issued_details += issued_by.name
                else:
                    issued_details += f"Unknown ({results[0]['IssuedByID']})"

                # Final message
                message = f"{subheader}\n**Reason**: {results[0]['Reason']}\n**Expires**: {expiry}\n{issued_details}"
                title = f"Case #{results[0]['CaseNo']}"
            else:
                title = f"Case #{case}"
                message = "*Case not found.*" #TODO: make an error?

            await interactions.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.USER_MANAGEMENT,
                title=title,
                message=message
            ).create())
            
        except Exception as e:
            await self.create_punishment_err(interactions,"display punishment",e)
            traceback.print_exc()
            return
        
    @app_commands.command(name="removecase", description="Removes the specified punishment case.")
    @app_commands.checks.has_role("Staff")
    @app_commands.describe(case="The case number.")
    async def removecase(self, interactions: discord.Interaction, case:app_commands.Range[int, 1, 999999]):

        try:
            with self.sql.get_connection() as connection:
                if self.sql.execute_query("SELECT * FROM Punishments WHERE CaseNo = %s",(case,),connection=connection,handle_except=False):
                    self.sql.execute_query("DELETE FROM Punishments WHERE CaseNo = %s",(case,),connection=connection,handle_except=False)

                    title=f"<:check:1346601762882326700> Case #{case} Removed"
                    message=f"**Case #{case}** has successfully been removed from the record."
                else:
                    raise NotFoundError(f"Punishment case #{case} could not be found.")
        except Exception as e:
            await self.create_punishment_err(interactions,"delete punishment",e)
            return

        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.USER_MANAGEMENT,
            title=title,
            message=message
        ).create())

    @app_commands.command(name="editcase", description="Edits the reason listed on the specified punishment case.")
    @app_commands.checks.has_role("Staff")
    @app_commands.describe(case="The case number.", reason="The updated reason.")
    async def editcase(self, interactions: discord.Interaction, case:app_commands.Range[int, 1, 999999], reason:str):

        try:
            with self.sql.get_connection() as connection:
                if self.sql.execute_query("SELECT * FROM Punishments WHERE CaseNo = %s",(case,),connection=connection,handle_except=False):
                    self.sql.execute_query("UPDATE Punishments SET Reason = %s WHERE CaseNo = %s",(reason, case),connection=connection,handle_except=False)

                    title=f"<:check:1346601762882326700> Case #{case} Edited"
                    message=f"**Case #{case}** has been updated with reason '*{reason}*'."
                else:
                    raise NotFoundError(f"Punishment case #{case} could not be found.")
        except Exception as e:
            await self.create_punishment_err(interactions,"edit punishment",e)
            return

        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.USER_MANAGEMENT,
            title=title,
            message=message
        ).create())