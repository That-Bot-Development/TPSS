import discord
from discord.ext import tasks, commands

from bot_client import Client
from modules.base import BaseModule, MemberNotFoundError
from modules.util.embed_maker import *
from modules.util.exceptions import *

from datetime import *
import asyncio

async def setup(client:Client, config):
    if config["sql_enabled"]:
        await client.add_cog(PunishmentSystem(client))

class PunishmentSystem(BaseModule):
    """Base class for the That Bot Punishment System"""

    async def commit_punishment(self, user_id:int, punishment_type:str, reason:str, issued_by_id:int, expires:datetime=None):
        if not self.client.sql:
            raise DatabaseError("SQL module is not initialized!")

        with self.client.sql.get_connection() as connection:
            self.client.sql.execute_query("""
                INSERT INTO Punishments (UserID, Type, Reason, IssuedByID, ExpiresAt) 
                VALUES (%s,%s,%s,%s,%s)
            """,(user_id,punishment_type,reason,issued_by_id,expires),connection=connection,handle_except=False)

            result = self.client.sql.execute_query("SELECT * FROM Punishments WHERE CaseNo = LAST_INSERT_ID()",connection=connection,handle_except=False)

        id = result[0]['CaseNo'] if result else "?"

        return id

    async def create_punishment_err(self, interactions:discord.Interaction, action:str, e:Exception):
        if isinstance(e, DatabaseError):
            message = "Unable to reach the database.\n\nIf the issue persists, contact an admin."
        elif isinstance(e,DurationParseError):
            message = "The duration could not be parsed.\nPlease ensure you follow the proper format:\n> m = Minutes, h = Hours, d = Days, w = Weeks, M = Months, y = Years\n*ex.* **2d 5h**"
        elif isinstance(e,DurationOutOfBoundsError):
            message = str(e)
        elif isinstance(e,MemberNotFoundError):
            message = "The user specified is not a member of the server!"
        elif isinstance(e,NotFoundError):
            message = str(e)
        elif isinstance(e,SelfPunishError):
            message = "You tried to punish yourself. Genius stuff."
        elif isinstance(e,PermissionError):
            message = "You cannot punish this user!"
        else:
            message = "This action could not be completed.\nPlease ensure you have the required permissions.\n\nIf the issue persists, contact an admin."

        print(f"Exception occured in '{action}' operation: {e}")
        await interactions.response.send_message(embed=self.client.embeds.create(
            embed_type=EmbedType.USER_MANAGEMENT,
            message=message,
            error=True
        ),ephemeral=True)
        
class ExpiredPunishmentManager(PunishmentSystem):
    '''Manages expired punishments'''

    @commands.Cog.listener()
    async def on_ready(self):
        await super().on_ready()

        if not self.unban_expired_tempbans.is_running():
            self.unban_expired_tempbans.start()
        #if not self.remove_expired_punishments.is_running():
         #   self.remove_expired_punishments.start()

    # NOTE: Not a fan of this implementation, could be done better if we had a 'expired' column for temp-bans
    @tasks.loop(minutes=1)
    async def unban_expired_tempbans(self):
        '''Removes all expires tempbans'''
        cur_datetime = datetime.now()

        results = self.client.sql.execute_query(
            "SELECT * FROM Punishments WHERE Type = 'temp-ban' AND ExpiresAt < %s AND ExpiresAt > %s",
            (cur_datetime,cur_datetime - timedelta(weeks=1))
        )

        if results:
            server:discord.Guild = self.client.d_consts.SERVER
            for row in results:
                try:
                    user:discord.User = await self.client.fetch_user(row['UserID'])
                    await server.unban(user)
                except Exception:
                   pass

    @tasks.loop(minutes=1) #TODO: Finish ts! 
    async def remove_expired_punishments(self):
        cur_datetime = datetime.now()

        with self.client.sql.get_connection() as connection:
            results = self.client.sql.execute_query(
                "SELECT * FROM Punishments WHERE Type != 'temp-ban' OR Type != 'ban' AND ExpiresAt < %s",
                (cur_datetime,cur_datetime - timedelta(weeks=8)),
                connection=connection
            )

            if results:
                for row in results:
                    try:
                        # TODO: Delete
                        pass
                        # TODO: Log!
                    except Exception:
                        pass                
            
class SelfPunishError(Exception):
    """Thrown when a user attempts to issue a punishment on themselves."""
    
    def __init__(self, user:discord.User, pun_type:str):
        super().__init__(f"{user.display_name} attempted to {pun_type} themselves.")

class SelfPunishError(Exception):
    """Thrown when a user attempts to issue a punishment on themselves."""
    
    def __init__(self, user:discord.User, pun_type:str):
        super().__init__(f"{user.display_name} attempted to {pun_type} themselves.")