import discord
from discord import app_commands
from discord.ext import commands

from bot_client import Client
from modules.base import MemberNotFoundError
from modules.user_management.punishment_system import PunishmentSystem, SelfPunishError
from modules.util.embed_maker import *
from modules.util.exceptions import DurationOutOfBoundsError, DurationParseError, PermissionError

from datetime import *

async def setup(client:Client, config):
    if config["sql_enabled"]:
        await client.add_cog(PunishmentCommands(client))

#TODO: Manage Members permission check failsafe (currently temporary solution)
#TODO: DEFER when using DB (pretty much everything here)
class PunishmentCommands(PunishmentSystem):
    def __init__(self, client: Client):
        self.client = client

    @app_commands.command(name="warn", description="Warns the specified member.")
    @app_commands.checks.has_role("Staff")
    @app_commands.describe(user="The member to be warned.", reason="The reason for the punishment.")
    async def warn(self, interactions: discord.Interaction, user:discord.User, reason:str):
        if not interactions.user.guild_permissions.moderate_members:
            return
        
        pun_type = "warn"

        try:
            # User MUST be a member of the server
            member = await self.get_member(user.id)

            await self.verify_punish_permissions(interactions.user,member,user.id,pun_type)

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
    @app_commands.describe(user="The member to be muted.", reason="The reason for the punishment.", duration="The length of the punishment. (m = Minutes, h = Hours, d = Days, w = Weeks)")
    async def mute(self, interactions: discord.Interaction, user:discord.User, reason:str, duration:str):
        pun_type = "mute"

        try:
            # User MUST be a member of the server
            member = await self.get_member(user.id)

            await self.verify_punish_permissions(interactions.user,member,user.id,pun_type)

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
    @app_commands.describe(user="The member to be kicked.", reason="The reason for the punishment.")
    async def kick(self, interactions: discord.Interaction, user:discord.User, reason:str):
        pun_type = "kick"

        try:
            # User MUST be a member of the server
            member = await self.get_member(user.id)

            await self.verify_punish_permissions(interactions.user,member,user.id,pun_type)
            
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
            await self.verify_punish_permissions(interactions.user,member,user.id,pun_type)
            
            if duration is not None:
                pun_type = "temp-ban"

                time = await self.duration_str_to_time(duration)

                expiry = datetime.now() + time

            # DM must be sent before banning the user from the server
            if member is not None:
                await self.send_punishment_dm(member,pun_type,reason,footer_message="If you feel as if your punishment should be removed, please fill out [this](https://forms.gle/ewMRCRny6RQMZxna9) form. Please be reasonable when submitting your appeal.")

            # Issue a Discord Ban on this user
            server:discord.Guild = self.client.d_consts.SERVER
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
    @app_commands.describe(user="The member to be unmuted.")
    async def unmute(self, interactions: discord.Interaction, user:discord.User):
        pun_type = "unmute"
        reason=f"Unmuted by {interactions.user.display_name}."

        try:
            # User MUST be a member of the server
            member = await self.get_member(user.id)

            await self.verify_punish_permissions(interactions.user,member,user.id,pun_type)

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
            await self.verify_punish_permissions(interactions.user,None,user.id,pun_type)
            
            # Remove Discord Ban on this user
            server:discord.Guild = self.client.d_consts.SERVER
            try:
                await server.unban(user, reason=reason)
            except Exception:
                # TODO: Raise error for user not banned?
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

    
    ## Punishment Helpers ##
    
    async def send_punishment_response(self, interactions:discord.Interaction, user:discord.User, punishment_type:str, punishment_id:str, reason:str, expiry:datetime = None):    
        cmd_response_message = f"**Case #{punishment_id}**: **{user.display_name}** has been {self.past_tense(punishment_type).lower()} with reason '*{reason}*'."

        if expiry is not None:
            try:
                expiry_f:str = expiry.strftime("%d/%m/%Y @ %H:%M:%S")
                cmd_response_message += f"\n\nThis punishment will expire on `{expiry_f}`."
            except Exception:
                pass

        await interactions.response.send_message(embed=self.client.embeds.create(
            embed_type=EmbedType.USER_MANAGEMENT,
            title=f"<:check:1346601762882326700> {punishment_type.capitalize()} Applied",
            message=cmd_response_message
        ))

    async def send_punishment_dm(self, member:discord.Member, punishment_type:str, reason:str, expiry:datetime=None, footer_message:str=''):
        try:
            message = f"**Reason**: {reason}"

            if expiry is not None:
                expiry_f:str = expiry.strftime("%d/%m/%Y @ %H:%M:%S")
                message += f"\nYour punishment will expire on `{expiry_f}`"

            message += f"\n{footer_message}"

            await member.send(embed=self.client.embeds.create(
                embed_type=EmbedType.USER_MANAGEMENT,
                title=f"<:alert:1346654360012329044> You have been {self.past_tense(punishment_type).lower()}" +
                    f"{' from That Place' if punishment_type in {'ban', 'kick'} else ''}.",
                message=message
            ))
        except Exception:
            pass

    async def to_punishment_logs(self, user:discord.User, punishment_type:str, punishment_id:str, reason:str=None, expiry:datetime=None):
        logs = self.client.d_consts.CHANNEL_MODLOGS

        if expiry is not None:
            expiry_f = f"`{expiry.strftime("%d/%m/%Y @ %H:%M:%S")}`"
        else:
            expiry_f = "Never"

        try:
            await logs.send(embed=self.client.embeds.create(
                embed_type=EmbedType.USER_MANAGEMENT,
                title=f"Case #{punishment_id}",
                message=f"**{user.name}** - {punishment_type.lower()}\n**Reason**: {reason}\n**Expires**: {expiry_f}"
            ))
        except Exception:
            # TODO: handle! (although I don't protect other message sends like this...)
            pass

    async def verify_punish_permissions(self, invoker:discord.Member, member:discord.Member|None, user_id:int, punishment_type:str):
        
            if invoker.id == user_id:
                raise SelfPunishError(invoker,punishment_type)
            
            if member is not None:
                if invoker.top_role <= member.top_role:
                    raise PermissionError(invoker,member,punishment_type)


    ## Internal Utilities ##
    
    async def duration_str_to_time(self, duration:str) -> timedelta:
        m = h = d = w = 0
        curNum = ""

        for char in duration:
            match(char):
                case _ if char.isnumeric():
                    curNum += char

                case 'm':
                    m += int(curNum)
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
