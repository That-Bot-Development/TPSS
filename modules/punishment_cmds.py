import discord
from discord import app_commands

from modules.punishment_system import PunishmentSystem, DurationOutOfBoundsError
from modules.util.embed_maker import *

from datetime import *

class PunishmentCommands(PunishmentSystem):
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
    @app_commands.describe(user="The user to be muted.", reason="The reason for the punishment.", duration="The length of the punishment. (m = Minutes, h = Hours, d = Days, w = Weeks)")
    async def mute(self, interactions: discord.Interaction, user:discord.User, reason:str, duration:str):
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
    @app_commands.describe(user="The user to be banned.", reason="The reason for the punishment.", duration="(optional) The length of the punishment. (m = Minutes, h = Hours, d = Days, w = Weeks, M = Months, y = Years)")
    async def kick(self, interactions: discord.Interaction, user:discord.User, reason:str, duration:str=None):
        pun_type = "ban"
        expiry = None

        member = await self.get_member(user.id)

        try:
            if duration is not None:
                pun_type = "temp-ban"

                time = await self.duration_str_to_time(duration)

                expiry = datetime.now() + time
                expiry = expiry.strftime('%Y-%m-%d %H:%M:%S')


            # DM must be sent before banning the user from the server
            await self.send_punishment_dm(member,pun_type,None,reason,footer_message="If you feel as if your punishment should be removed, please fill out [this](https://forms.gle/ewMRCRny6RQMZxna9) form. Please be reasonable when submitting your appeal.")

            # Issue a Discord Ban on this user
            await member.ban(reason=reason)

            # Commit to database
            id = None
            id = await self.commit_punishment(
                user_id=member.id,
                punishment_type=pun_type,
                reason=reason,
                issued_by_id=interactions.user.id,
                expires=expiry
            )
        except Exception as e:
            await self.create_punishment_err(interactions,pun_type,e)
            return

        await self.respond_and_log_punishment(interactions,(pun_type,id),member,None,reason,handle_dm=False)