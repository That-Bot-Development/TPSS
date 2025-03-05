import discord
from discord import app_commands
from datetime import *

from modules.base import BaseModule
from modules.util.embed_maker import *


class PunishmentCommands(BaseModule):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="mute", description="Mutes the specified user.")
    @app_commands.describe(user="The user to be muted.",duration="The length of the punishment. (m = Minutes, h = Hours, d = Days, w = Weeks, M = Months)", reason="The reason for the punishment.")
    async def mute(self, interactions: discord.Interaction, user:discord.User, duration:str, reason:str):
        time = await self.duration_str_to_time(interactions,duration)
        member = await self.get_member(user)
        try:
            await member.timeout(time,reason=reason)
        except Exception as e:
            await self.create_punishment_err(interactions,"mute",e)
            return
        
        await self.create_punishment_success_msg(interactions,"mute",member,member.timed_out_until,reason)
        # TODO: Embed Formatting
        # TODO: Link to Logging System
        # TODO: Link to Punishment Logging System

    # PUNISHMENT COMMAND UTILS


    async def create_punishment_err(self, interactions:discord.Interaction, punishment_type:str, e:Exception):
        print(f"Exception occured in '{punishment_type}' operation: {e}")
        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.USER_MANAGEMENT,
            message="The user could not be punished.\nPlease ensure you have the required permissions.\n\nIf the issue persists, contact an admin.",
            error=True
        ).create(),ephemeral=True,delete_after=20)

    async def create_punishment_success_msg(self, interactions:discord.Interaction, punishment_type:str, member:discord.Member, expiry:datetime, reason:str):
        punishment_type = punishment_type.capitalize()
        expiry_f:str = expiry.strftime("%d/%m/%Y @ %H:%M:%S")
        await interactions.response.send_message(embed=EmbedMaker(
            embed_type=EmbedType.USER_MANAGEMENT,
            title=f"<:check:1346601762882326700> {punishment_type} Applied",
            message=f"{punishment_type} applied to **{member.display_name}** with reason '*{reason}*'.\n\nThis punishment will expire on `{expiry_f}`"
        ).create())

    async def get_member(self, user:discord.User) -> discord.Member:
        server:discord.Guild = self.d_consts.SERVER
        return server.get_member(user.id) or await server.fetch_member(user.id)

    
    async def duration_str_to_time(self, interactions: discord.Interaction, duration:str) -> timedelta:
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
                        w += int(curNum)*4
                    case ' ':
                        pass
                    case _:
                        raise Exception("Could not parse duration")
            except Exception as e:
                print(f"Exception occured in 'punishment duration processing' operation: {e}")
                await interactions.response.send_message(embed=EmbedMaker(
                    embed_type=EmbedType.USER_MANAGEMENT,
                    message="The duration could not be parsed.\nPlease ensure you follow the provided format:\n> m = Minutes, h = Hours, d = Days, w = Weeks, M = Months\n*ex.* **2d 5h**",
                    error=True

                    
                ).create(),ephemeral=True,delete_after=20)
                break

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
