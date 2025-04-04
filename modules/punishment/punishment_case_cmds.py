import discord
from discord import app_commands

from modules.punishment.punishment_system import PunishmentSystem
from modules.util.embed_maker import *

import traceback
from datetime import *


class PunishmentCaseCommands(PunishmentSystem):
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
                    for row in results:
                        message += f"**Case #{row['CaseNo']}** - {row['Type']}\n{row['Reason']}\n-# {datetime.strptime(str(row['IssuedAt']),"%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")}\n\n"
                else:
                    message = "*No cases found.*"
        except Exception as e:
            await self.create_punishment_err(interactions,"list punishments",e)
            return

        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.USER_MANAGEMENT,
            title=f"Punishments: {self.truncate_string(user.name)}",
            message=message
        ).create())

    @app_commands.command(name="case", description="View a specific punishment case.")
    @app_commands.describe(case="The case number.")
    async def case(self, interactions: discord.Interaction, case:app_commands.Range[int, 1, 999999]):        
        try:
            with self.sql.get_connection() as connection:
                results = self.sql.execute_query("SELECT * FROM Punishments WHERE CaseNo = %s",(case,),connection=connection,handle_except=False)

            if results:
                # Sub-header
                user = await self.client.fetch_user(results[0]['UserID'])
                if user is not None:
                    subheader = f"**{user.name}** ({user.id})"
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
                message = "*No cases found.*" #TODO: make an error?

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
                    title = f"Case #{case}"        #TODO: make error? (prolly yea, maybe have it a normal message still though idk)            
                    message = "*Case not found.*"
        except Exception as e:
            await self.create_punishment_err(interactions,"delete punishment",e)
            return

        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.USER_MANAGEMENT,
            title=title,
            message=message
        ).create())

    # TODO: Move to some sort of utilities class? Probably also true for the function I just moved to base
    def truncate_string(self, text, max_length=16):
        """Truncates a string and adds ellipsis if it exceeds max_length."""
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text