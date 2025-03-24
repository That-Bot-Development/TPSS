import discord
from discord import app_commands

from modules.base import BaseModule
from modules.util.embed_maker import *
from modules.util.sql_manager import SQLManager

import traceback
from datetime import *
from mysql.connector import Error as sql_error

class PunishmentCommands(BaseModule): # TODO: Split (yes)
    def __init__(self, client):
        self.client = client

    # TODO: Check on incorrect dates in DB, see pinned
    @app_commands.command(name="mute", description="Mutes the specified user.")
    @app_commands.describe(user="The user to be muted.",duration="The length of the punishment. (m = Minutes, h = Hours, d = Days, w = Weeks, M = Months)", reason="The reason for the punishment.")
    async def mute(self, interactions: discord.Interaction, user:discord.User, duration:str, reason:str):
        pun_type = "mute"

        member = await self.get_member(user.id)

        # Issue a Discord Timeout on this user
        try:
            time = await self.duration_str_to_time(duration)

            await member.timeout(time,reason=reason)

            id = None
            id = await self.commit_punishment(
                user_id=member.id,
                punishment_type=pun_type,
                reason=reason,
                issued_by_id=interactions.user.id
                ,expires=member.timed_out_until.strftime('%Y-%m-%d %H:%M:%S')
            
            )
        except Exception as e:
            await self.create_punishment_err(interactions,pun_type,e)
            await member.timeout(0,reason="Internal Error. Cancelling.") # Cancel the punishment
            return


        await self.create_punishment_success_msg(interactions,(pun_type,id),member,member.timed_out_until,reason)
        # TODO: Link to Logging System

    # TODO: Why is this not loading now??
    @app_commands.command(name="punishments", description="Lists all punishment cases for the specified user.")
    @app_commands.describe(user="The user to check punishments on.")
    async def punishments(self, interactions: discord.Interaction, user:discord.User=None):
        if user is None:
            member = interactions.user
        else:
            member = await self.get_member(user.id)

        message = ""

        try:
            connection = self.sql.get_connection()

            results = self.sql.execute_query("SELECT * FROM Punishments WHERE UserID = %s",(member.id,),connection=connection,handle_except=False)

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
            title=f"Punishments: {self.truncate_string(member.display_name)}",
            message=message
        ).create())

    @app_commands.command(name="case", description="View a specific punishment case.")
    @app_commands.describe(case="The case number.")
    async def punishments(self, interactions: discord.Interaction, case:int):        
        message = title = ""
        member = None

        try:
            connection = self.sql.get_connection()

            results = self.sql.execute_query("SELECT * FROM Punishments WHERE CaseNo = %s",(case,),connection=connection,handle_except=False)

            if results:
                # Get Member #TODO: Is there a better & less verbose way of doing this & subheader
                try:
                    member = await self.get_member(results[0]['UserID'])
                except Exception as e:
                    pass
                
                # Sub-header
                if member is not None:
                    message = f"**{member.name}** ({member.id}) \- {results[0]['Type']}\n\n"
                else:
                    message = f"**Unknown** ({results[0]['UserID']}) \- {results[0]['Type']}\n\n"

                issued_by =  await self.get_member(results[0]['IssuedByID']) # TODO: Temporary, needs to be moved to the issuedby verification

                # Body  TODO: (define once expired logic in)
                message += f"**Reason**: {results[0]['Reason']}\n**Expires**: Never\n\n-# Issued {datetime.strptime(str(results[0]['IssuedAt']),"%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")} by {issued_by.name}"
                # TODO: Expired logic TODO: IssuedBy validity verification TODO: Fix formatting idk wtf
                title = f"Case #{results[0]['CaseNo']}"
            else:
                message = "*Case not found.*" # TODO: Make an error?
                title = f"Case #{case}"

            await interactions.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.USER_MANAGEMENT,
                title=title,
                message=message
            ).create())
            
        except Exception as e:
            await self.create_punishment_err(interactions,"display punishment",e)
            traceback.print_exc()
            return

    # TODO: Move to some sort of utilities function? Probably also true for the function Ijust moved to base
    def truncate_string(self, text, max_length=16):
        """Truncates a string and adds ellipsis if it exceeds max_length."""
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text


    # PUNISHMENT COMMAND INTERNAL FUNCTIONS

    async def commit_punishment(self, user_id:int, punishment_type:str, reason:str, issued_by_id:int, expires:datetime=None):
        connection = self.sql.get_connection()
        
        try:
            self.sql.execute_query("""
                INSERT INTO Punishments (UserID, Type, Reason, IssuedByID, ExpiresAt) 
                VALUES (%s,%s,%s,%s,%s)
            """,(user_id,punishment_type,reason,issued_by_id,expires),connection=connection,handle_except=False)

            result = self.sql.execute_query("SELECT * FROM Punishments WHERE CaseNo = LAST_INSERT_ID()",connection=connection)
        except sql_error as e:
            raise

        id = result[0]['CaseNo'] if result else "?"

        return id

    async def create_punishment_err(self, interactions:discord.Interaction, action:str, e:Exception):
        is_query_error = isinstance(e, sql_error)
        if isinstance(e, sql_error):
            message = "Unable to reach the database.\n\nIf the issue persists, contact an admin."
        elif isinstance(e,DurationParseError):
            message = "The duration could not be parsed.\nPlease ensure you follow the provided format:\n> m = Minutes, h = Hours, d = Days, w = Weeks, M = Months\n*ex.* **2d 5h**"
        else:
            message = "This action could not be completed.\nPlease ensure you have the required permissions.\n\nIf the issue persists, contact an admin."

        print(f"Exception occured in '{action}' operation: {e}")
        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.USER_MANAGEMENT,
            message=message,
            error=True
        ).create(),ephemeral=True,delete_after=20)

    async def create_punishment_success_msg(self, interactions:discord.Interaction, punishment_info:tuple, member:discord.Member, expiry:datetime, reason:str):
        punishment_type = punishment_info[0].capitalize()
        punishment_id = punishment_info[1]
        
        expiry_f:str = expiry.strftime("%d/%m/%Y @ %H:%M:%S")
        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.USER_MANAGEMENT,
            title=f"<:check:1346601762882326700> {punishment_type} Applied",
            message=f"**Case #{punishment_id}**: {punishment_type} applied to **{member.display_name}** with reason '*{reason}*'.\n\nThis punishment will expire on `{expiry_f}`"
        ).create())
    
    async def duration_str_to_time(self, duration:str) -> timedelta:
        m = h = d = w = 0
        curNum = ""

        for char in duration:
            print(char)
            try:
                match(char):
                    case _ if char.isnumeric():
                        curNum += char
                        print("Numeric")

                    case 'm':
                        m += int(curNum)
                        print("Minute")
                    case _ if char.lower() == 'h':
                        h += int(curNum)
                    case _ if char.lower() == 'd':
                        d += int(curNum)
                    case _ if char.lower() == 'w':
                        w += int(curNum)
                    case 'M':
                        # Timedelta does not support Months, this must be converted manually
                        # TODO: Doesn't work
                        w += int(curNum)*4
                    case ' ':
                        pass
                    case _:
                        raise Exception("Could not parse duration")
            except Exception as e:
                raise DurationParseError("Could not parse punishment duration from user input")

            # Reset current number once the value has been added to its respective category
            if (char.isalpha()):
                curNum = ""

        return timedelta(
            weeks=w,
            days=d,
            hours=h,
            minutes=m,
            seconds=0
        )

class DurationParseError(Exception):
    """Thrown when punishment duration cannot be parsed from user input."""
    pass