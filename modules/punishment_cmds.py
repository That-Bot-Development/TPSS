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

    @app_commands.command(name="warn", description="Warns the specified user.")
    @app_commands.describe(user="The user to be warned.", reason="The reason for the punishment.")
    async def warn(self, interactions: discord.Interaction, user:discord.User, reason:str):
        pun_type = "warn"

        member = await self.get_member(user.id)

        try:
            # Commit to database
            id = None
            id = await self.commit_punishment(
                user_id=member.id,
                punishment_type=pun_type,
                reason=reason,
                issued_by_id=interactions.user.id,
                expires=None
            )
        except Exception as e:
            await self.create_punishment_err(interactions,pun_type,e)
            return

        await self.respond_and_log_punishment(interactions,(pun_type,id),member,None,reason)
    
    
    # TODO: Check on incorrect dates in DB, see pinned
    @app_commands.command(name="mute", description="Mutes the specified user.")
    @app_commands.describe(user="The user to be muted.", duration="The length of the punishment. (m = Minutes, h = Hours, d = Days, w = Weeks)", reason="The reason for the punishment.")
    async def mute(self, interactions: discord.Interaction, user:discord.User, duration:str, reason:str):
        pun_type = "mute"

        member = await self.get_member(user.id)

        try:
            time = await self.duration_str_to_time(duration)

            if time > timedelta(days=28) or time < timedelta(0):
                raise DurationOutOfBoundsError("Mute duration cannot exceed 28 days or be negative.")

            # Issue a Discord Timeout on this user
            await member.timeout(time,reason=reason)

            # Commit to database
            id = None
            id = await self.commit_punishment(
                user_id=member.id,
                punishment_type=pun_type,
                reason=reason,
                issued_by_id=interactions.user.id,
                expires=member.timed_out_until.strftime('%Y-%m-%d %H:%M:%S')
            )
        except Exception as e:
            await self.create_punishment_err(interactions,pun_type,e)
            await member.timeout(timedelta(0),reason="Internal Error. Cancelling.") # Cancel the punishment
            return

        await self.respond_and_log_punishment(interactions,(pun_type,id),member,member.timed_out_until,reason)

    @app_commands.command(name="kick", description="Kicks the specified user.")
    @app_commands.describe(user="The user to be kicked.", reason="The reason for the punishment.")
    async def kick(self, interactions: discord.Interaction, user:discord.User, reason:str):
        pun_type = "kick"

        member = await self.get_member(user.id)

        try:
            # DM must be sent before kicking the user from the server
            await self.send_punishment_dm(member,pun_type,None,reason)

            # Issue a Discord Kick on this user
            await member.kick(reason=reason)

            # Commit to database
            id = None
            id = await self.commit_punishment(
                user_id=member.id,
                punishment_type=pun_type,
                reason=reason,
                issued_by_id=interactions.user.id,
                expires=None
            )
        except Exception as e:
            await self.create_punishment_err(interactions,pun_type,e)
            return

        await self.respond_and_log_punishment(interactions,(pun_type,id),member,None,reason,handle_dm=False)

    @app_commands.command(name="ban", description="Bans the specified user.")
    @app_commands.describe(user="The user to be banned.", reason="The reason for the punishment.")
    async def kick(self, interactions: discord.Interaction, user:discord.User, reason:str):
        pun_type = "ban"

        member = await self.get_member(user.id)

        try:
            # DM must be sent before banning the user from the server
            #TODO: Replace with specific ban DM prolly
            await self.send_punishment_dm(member,pun_type,None,reason)

            # Issue a Discord Ban on this user
            await member.ban(reason=reason)

            # Commit to database
            id = None
            id = await self.commit_punishment(
                user_id=member.id,
                punishment_type=pun_type,
                reason=reason,
                issued_by_id=interactions.user.id,
                expires=None
            )
        except Exception as e:
            await self.create_punishment_err(interactions,pun_type,e)
            return

        await self.respond_and_log_punishment(interactions,(pun_type,id),member,None,reason,handle_dm=False)

    @app_commands.command(name="punishments", description="Lists all punishment cases for the specified user.")
    @app_commands.describe(user="The user to check punishments on.")
    async def punishments(self, interactions: discord.Interaction, user:discord.User=None):
        if user is None:
            member = interactions.user
        else:
            member = await self.get_member(user.id)

        message = ""

        try:
            with self.sql.get_connection() as connection:
                #TODO: Re-evaluate if I need to be creating an independent connection when I am only executing one query in the function
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
    async def case(self, interactions: discord.Interaction, case:int):        
        message = title = ""
        member = None

        try:
            with self.sql.get_connection() as connection:
                results = self.sql.execute_query("SELECT * FROM Punishments WHERE CaseNo = %s",(case,),connection=connection,handle_except=False)

            if results:
                # Sub-header
                member = await self.get_member(results[0]['UserID'])
                if member is not None:
                    subheader = f"**{member.name}** ({member.id})"
                else:
                    subheader = f"**Unknown** ({results[0]['UserID']})"
                subheader += f" - {results[0]['Type']}"

                # Expiry
                expires_on = results[0]['ExpiresAt']
                if expires_on is not None:
                    expiry = f"{datetime.strptime(str(results[0]['ExpiresAt']),"%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")}"
                else:
                    expiry = "Never"

                # Details on issuance of punishment
                issued_by =  await self.get_member(results[0]['IssuedByID'])
                issued_details = f"-# Issued {datetime.strptime(str(results[0]['IssuedAt']),"%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")} by "
                if issued_by is not None:
                    issued_details += issued_by.name
                else:
                    issued_details += f"Unknown ({results[0]['IssuedByID']})"

                # Final message
                message = f"{subheader}\n**Reason**: {results[0]['Reason']}\n**Expires**: {expiry}\n{issued_details}"
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

    # TODO: Move to some sort of utilities class? Probably also true for the function I just moved to base
    def truncate_string(self, text, max_length=16):
        """Truncates a string and adds ellipsis if it exceeds max_length."""
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text


    # PUNISHMENT COMMAND INTERNAL FUNCTIONS

    async def commit_punishment(self, user_id:int, punishment_type:str, reason:str, issued_by_id:int, expires:datetime=None):
        try:
            with self.sql.get_connection() as connection:
                self.sql.execute_query("""
                    INSERT INTO Punishments (UserID, Type, Reason, IssuedByID, ExpiresAt) 
                    VALUES (%s,%s,%s,%s,%s)
                """,(user_id,punishment_type,reason,issued_by_id,expires),connection=connection,handle_except=False)

                result = self.sql.execute_query("SELECT * FROM Punishments WHERE CaseNo = LAST_INSERT_ID()",connection=connection,handle_except=False)
        except sql_error:
            raise

        id = result[0]['CaseNo'] if result else "?"

        return id

    async def create_punishment_err(self, interactions:discord.Interaction, action:str, e:Exception):
        if isinstance(e, sql_error):
            message = "Unable to reach the database.\n\nIf the issue persists, contact an admin."
        elif isinstance(e,DurationParseError):
            message = "The duration could not be parsed.\nPlease ensure you follow the proper format:\n> m = Minutes, h = Hours, d = Days, w = Weeks, M = Months, y = Years\n*ex.* **2d 5h**"
        elif isinstance(e,DurationOutOfBoundsError):
            message = str(e)
        else:
            message = "This action could not be completed.\nPlease ensure you have the required permissions.\n\nIf the issue persists, contact an admin."

        print(f"Exception occured in '{action}' operation: {e}")
        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.USER_MANAGEMENT,
            message=message,
            error=True
        ).create(),ephemeral=True,delete_after=20)
        
    async def respond_and_log_punishment(self, interactions:discord.Interaction, punishment_info:tuple, member:discord.Member, expiry:datetime, reason:str, handle_dm=True):
        punishment_type:str = punishment_info[0].lower()
        punishment_id:str = punishment_info[1]
        
        cmd_response_message = f"**Case #{punishment_id}**: **{member.display_name}** has been {self.past_tense(punishment_type)} with reason '*{reason}*'."

        if expiry is not None:
            try:
                expiry_f:str = expiry.strftime("%d/%m/%Y @ %H:%M:%S")
                cmd_response_message += f"\n\nThis punishment will expire on `{expiry_f}`"
            except Exception:
                pass

        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.USER_MANAGEMENT,
            title=f"<:check:1346601762882326700> {punishment_type.capitalize()} Applied",
            message=cmd_response_message
        ).create())

        # TODO: Link to Logging System

        if handle_dm:
            await self.send_punishment_dm(member,punishment_type,expiry,reason)

    async def send_punishment_dm(self, member:discord.Member, punishment_type:str, expiry:datetime, reason:str):
        try:
            user_dm_message = f"**Reason**: {reason}"

            if expiry is not None:
                expiry_f:str = expiry.strftime("%d/%m/%Y @ %H:%M:%S")
                user_dm_message += f"\nYour punishment will expire on `{expiry_f}`"

            await member.send(embed=EmbedMaker(
                embed_type=EmbedType.USER_MANAGEMENT,
                title=f"<:alert:1346654360012329044> You have been {self.past_tense(punishment_type)}.",
                message=user_dm_message
            ).create())
        except Exception:
            pass
    
    async def duration_str_to_time(self, duration:str) -> timedelta:
        m = h = d = w = 0
        curNum = ""

        for char in duration:
            try:
                match(char):
                    case _ if char.isnumeric():
                        curNum += char

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
                        w += int(curNum)*4
                    case 'y':
                        w += int(curNum)*52
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
    
    # Returns the past tense version of the very provided (only for the purpose of punishment types)
    def past_tense(self, verb):
        if verb.endswith("e"):
            return verb + "d"
        if verb.endswith("n"):
            return verb + "ned"
        else:
            return verb + "ed"

class DurationParseError(Exception):
    """Thrown when punishment duration cannot be parsed from user input."""
    pass

class DurationOutOfBoundsError(Exception):
    """Thrown when the specified duration is out of bounds for the given context."""
    pass