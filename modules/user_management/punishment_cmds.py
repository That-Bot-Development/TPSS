import discord
from discord import app_commands

from modules.base import MemberNotFoundError
from modules.user_management.punishment_system import PunishmentSystem, SelfPunishError
from modules.util.embed_maker import *
from modules.util.exceptions import DurationOutOfBoundsError, PermissionError

from datetime import *

#TODO: Manage Members permission check failsafe (currently temporary solution)
class PunishmentCommands(PunishmentSystem):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="warn", description="Warns the specified member.")
    @app_commands.checks.has_role("Staff")
    @app_commands.describe(member="The member to be warned.", reason="The reason for the punishment.")
    async def warn(self, interactions: discord.Interaction, user:discord.User, reason:str):
        if not interactions.user.guild_permissions.moderate_members:
            return
        
        pun_type = "warn"

        try:
            # User MUST be a member of the server
            member = await self.get_member(user.id)

            if interactions.user.id == member.id:
                raise SelfPunishError(interactions.user,pun_type)
            # NOTE: Allowed by Default (because it's funny) -
            # elif interactions.user.top_role <= member.top_role:
            #    raise PermissionError(interactions.user,member,pun_type)

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

        await self.send_punishment_response(interactions,member,pun_type,id,reason)
        await self.send_punishment_dm(member,pun_type,reason)
        await self.to_punishment_logs(member,pun_type,id,reason)

    
    # TODO: Check on incorrect dates in DB, see pinned
    @app_commands.command(name="mute", description="Mutes the specified member.")
    @app_commands.checks.has_role("Staff")
    @app_commands.describe(member="The member to be muted.", reason="The reason for the punishment.", duration="The length of the punishment. (m = Minutes, h = Hours, d = Days, w = Weeks)")
    async def mute(self, interactions: discord.Interaction, user:discord.User, reason:str, duration:str):
        pun_type = "mute"

        try:
            # User MUST be a member of the server
            member = await self.get_member(user.id)

            if interactions.user.id == member.id:
                raise SelfPunishError(interactions.user,pun_type)
            elif interactions.user.top_role <= member.top_role:
                raise PermissionError(interactions.user,member,pun_type)

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

        await self.send_punishment_response(interactions,member,pun_type,id,reason, member.timed_out_until)
        await self.send_punishment_dm(member,pun_type,reason,member.timed_out_until)
        await self.to_punishment_logs(member,pun_type,id,reason,member.timed_out_until)


    @app_commands.command(name="kick", description="Kicks the specified member.")
    @app_commands.checks.has_role("Staff")
    @app_commands.describe(member="The member to be kicked.", reason="The reason for the punishment.")
    async def kick(self, interactions: discord.Interaction, user:discord.User, reason:str):
        pun_type = "kick"

        try:
            # User MUST be a member of the server
            member = await self.get_member(user.id)

            if interactions.user.id == member.id:
                raise SelfPunishError(interactions.user,pun_type)
            elif interactions.user.top_role <= member.top_role:
                raise PermissionError(interactions.user,member,pun_type)
            
            # DM must be sent before kicking the user from the server
            await self.send_punishment_dm(member,pun_type,reason)

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

        await self.send_punishment_response(interactions,member,pun_type,id,reason)
        await self.to_punishment_logs(member,pun_type,id,reason)


    @app_commands.command(name="ban", description="Bans the specified user.")
    @app_commands.checks.has_role("Staff")
    @app_commands.describe(user="The user to be banned.", reason="The reason for the punishment.", duration="(optional) The length of the punishment. (m = Minutes, h = Hours, d = Days, w = Weeks, M = Months, y = Years)")
    async def ban(self, interactions: discord.Interaction, user:discord.User, reason:str, duration:str=None):
        pun_type = "ban"
        expiry = None

        try:
            member = await self.get_member(user.id)
        except MemberNotFoundError:
            member = None

        try:
            if interactions.user.id == member.id:
                raise SelfPunishError(interactions.user,pun_type)
            elif member is not None and interactions.user.top_role <= member.top_role:
                raise PermissionError(interactions.user,member,pun_type)
            
            if duration is not None:
                pun_type = "temp-ban"

                time = await self.duration_str_to_time(duration)

                expiry = datetime.now() + time

            # DM must be sent before banning the user from the server
            if member is not None:
                await self.send_punishment_dm(member,pun_type,reason,footer_message="If you feel as if your punishment should be removed, please fill out [this](https://forms.gle/ewMRCRny6RQMZxna9) form. Please be reasonable when submitting your appeal.")

            # Issue a Discord Ban on this user
            server:discord.Guild = self.d_consts.SERVER
            try:
                await server.ban(user, reason=reason)
            except Exception:
                # TODO: Handle this (see what causes, should only be when user is already banned (?)) 
                pass

            # Commit to database
            id = None
            id = await self.commit_punishment(
                user_id=user.id,
                punishment_type=pun_type,
                reason=reason,
                issued_by_id=interactions.user.id,
                expires=expiry
            )
        except Exception as e:
            await self.create_punishment_err(interactions,pun_type,e)
            return

        await self.send_punishment_response(interactions,user,pun_type,id,reason,expiry)
        await self.to_punishment_logs(user,pun_type,id,reason,expiry)

    # Punishment Removal Commands

    @app_commands.command(name="unmute", description="Unmutes the specified user.")
    @app_commands.checks.has_role("Staff")
    @app_commands.describe(member="The member to be unmuted.")
    async def unmute(self, interactions: discord.Interaction, member:discord.Member):
        pun_type = "unmute"
        reason=f"Unmuted by {interactions.user.display_name}."

        try:
            if interactions.user.id == member.id:
                raise SelfPunishError(interactions.user,pun_type)

            # Remove Discord Timeout on this user
            await member.timeout(timedelta(seconds=0),reason=reason)

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

        # Unmute PMs are handled by another bot that keeps track of automatic unmutes
        await self.send_punishment_response(interactions,member,pun_type,id,reason)
        await self.to_punishment_logs(member,pun_type,id,reason)


    @app_commands.command(name="unban", description="Unban the specified user.")
    @app_commands.checks.has_role("Staff")
    @app_commands.describe(user="The user to be unbanned.")
    async def unban(self, interactions: discord.Interaction, user:discord.User):
        pun_type = "unban"
        reason=f"Unbanned by {interactions.user.display_name}"

        try:
            if interactions.user.id == user.id:
                raise SelfPunishError(interactions.user,pun_type)
            
            # Remove Discord Ban on this user
            server:discord.Guild = self.d_consts.SERVER
            try:
                await server.unban(user, reason=reason)
            except Exception:
                # TODO: Raise error for user not banned
                print("Not banned")
                pass

            #TODO: Check what exception is thrown if user isnt found here
            # Commit to database
            id = None
            id = await self.commit_punishment(
                user_id=user.id,
                punishment_type=pun_type,
                reason=reason,
                issued_by_id=interactions.user.id,
                expires=None
            )
        except Exception as e:
            await self.create_punishment_err(interactions,pun_type,e)
            return

        await self.send_punishment_response(interactions,user,pun_type,id,reason)
        await self.to_punishment_logs(user,pun_type,id,reason)
