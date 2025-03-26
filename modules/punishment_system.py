import discord
from discord.ext import tasks

from modules.base import BaseModule
from modules.util.embed_maker import *

from datetime import *
from mysql.connector import Error as sql_error
import asyncio

class PunishmentSystem(BaseModule):
    """Base class for the That Bot Punishment System"""

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
        punishment_type:str = punishment_info[0]
        punishment_id:str = punishment_info[1]
        
        cmd_response_message = f"**Case #{punishment_id}**: **{member.display_name}** has been {self.past_tense(punishment_type).lower()} with reason '*{reason}*'."

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

    async def send_punishment_dm(self, member:discord.Member, punishment_type:str, expiry:datetime, reason, footer_message=''):
        try:
            message = f"**Reason**: {reason}"

            if expiry is not None:
                expiry_f:str = expiry.strftime("%d/%m/%Y @ %H:%M:%S")
                message += f"\nYour punishment will expire on `{expiry_f}`"

            message += f"\n{footer_message}"

            await member.send(embed=EmbedMaker(
                embed_type=EmbedType.USER_MANAGEMENT,
                title=f"<:alert:1346654360012329044> You have been {self.past_tense(punishment_type).lower()}" +
                    f"{' from That Place' if punishment_type in {'ban', 'kick'} else ''}.",
                message=message
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
        if verb.endswith("ban"):
            return verb + "ned"
        else:
            return verb + "ed"
        
# TODO: Register as cog once done
class ExpiredPunishmentManager(PunishmentSystem):
    '''Manages expired punishments'''

    def __init__(self):
        self.unban_expired_tempbans.start()
        self.remove_expired_punishments.start()

    @tasks.loop(hours=1)
    async def unban_expired_tempbans(self):
        '''Removes all expires tempbans'''
        while True:
            cur_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            results = self.sql.execute_query(
                "SELECT * FROM Punishments WHERE Type = 'temp-ban' AND ExpiresAt < %s AND ExpiresAt > %s",
                (cur_datetime,cur_datetime - timedelta(weeks=1)),
            )

            for row in results:
                try:
                    member:discord.Member = self.get_member(row['UserID'])

                    member.unban("Automatic Unban - Ban Expired")

                    #TODO: Log!
                except Exception:
                    #TODO: Handle!
                    pass

    @tasks.loop(hours=1)
    async def remove_expired_punishments(self):
        while True:
            cur_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with self.sql.get_connection() as connection:
                results = self.sql.execute_query(
                    "SELECT * FROM Punishments WHERE Type != 'temp-ban' OR Type != 'ban' AND ExpiresAt < %s",
                    (cur_datetime,cur_datetime - timedelta(weeks=8)),
                    connection=connection
                )

                for row in results:
                    try:
                        # TODO: Delete
                        pass
                        # TODO: Log!
                    except Exception:
                        pass

            await asyncio.sleep(3600)
                
        
class DurationParseError(Exception):
    """Thrown when punishment duration cannot be parsed from user input."""
    pass

class DurationOutOfBoundsError(Exception):
    """Thrown when the specified duration is out of bounds for the given context."""
    pass