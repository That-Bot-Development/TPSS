import discord
from discord import app_commands
from datetime import timedelta

from modules.base import BaseModule
from util.embed_maker import *


class PunishmentCommands(BaseModule):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="mute", description="Mutes the specified user.")
    @app_commands.describe(user="The user to be muted.",duration="The length of the punishment. (m = Minutes, h = Hours, d = Days, w = Weeks, M = Months )", reason="The reason for the punishment.")
    async def mute(self, interactions: discord.Interaction, user:discord.User, duration:str, reason:str):
        time = await self.duration_str_to_time(interactions,duration)
        member = await self.get_member(user)
        await member.timeout(time,reason=reason)
        # TODO: Embed Formatting
        # TODO: Link to Logging System
        # TODO: Link to Punishment Logging System

    # PUNISHMENT COMMAND UTILS

    async def get_member(self, user:discord.User) -> discord.Member:
        server:discord.Guild = self.d_consts.SERVER
        return server.get_member(user.id) or await server.fetch_member(user.id)

    
    async def duration_str_to_time(self, interactions: discord.Interaction, duration:str) -> timedelta:
        m = h = d = w = M = 0
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
                        M += int(curNum)
                    case _:
                        raise Exception("Could not parse duration")
            except Exception as e:
                print(f"Exception occured in 'punishment duration processing' operation: {e}")
                await interactions.response.send_message(EmbedMaker(
                        embed_type=EmbedType.PUNISHMENT_CMD,
                        message="The duration could not be parsed.\nPlease ensure you follow the format provided",
                        title="err"
                    ).create()
                )
                break

            # Reset current number once the value has been added to its respective category
            if (char.isalpha()):
                curNum = ""


        # Timedelta does not support Months, this must be converted manually
        w += M*4

        return timedelta(
            weeks=w,
            days=d,
            hours=h,
            minutes=m,
            seconds=0
        )
