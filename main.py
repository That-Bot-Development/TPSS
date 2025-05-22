import discord
import asyncio

from discord import app_commands
from discord.ext import commands

# Utility modules that require set-up here
import modules.util.discord_const as d_consts
import modules.util.sql_manager as sql

# Modules
import modules.base as base
import modules.modmail.mod_mail as mm
import modules.ban_dm as bd
import modules.suggestion_manager as sm
import modules.art_manager as am
import modules.user_management.punishment_system as ps
import modules.user_management.punishment_cmds as pc
import modules.user_management.punishment_case_cmds as pcc
import modules.user_management.staff_notes as sn
import modules.fun as f
import modules.utilities as u

debug = False

# Set up bot
GUID = discord.Object(id=578356230637223936)
intents = discord.Intents.all() 

class aClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents,command_prefix="db_tpss!")
        print("Started up!")
    async def setup_hook(self):
        self.tree.copy_global_to(guild=GUID)
        await self.tree.sync(guild=GUID)

client = aClient(intents=intents)

async def getToken():
     with open('private/token.txt', 'r') as file:
        token = file.readline()
        return token

# Initialize cogs
async def init_cogs():
    # Instantiate utilities & initialize reference vars
    await client.add_cog(d_consts.DiscordConstants(client))

    base.BaseModule.d_consts = d_consts.DiscordConstants.get() #NOTE: Sometimes d_consts loads late
    base.BaseModule.sql = sql.SQLManager()

    # Initialize cogs TODO: Rework this at some point (and above)
    if not debug:
        await client.add_cog(mm.ModMail(client))
        await client.add_cog(bd.BanDM(client))
        await client.add_cog(sm.SuggestionManager(client))
        await client.add_cog(am.ArtManager(client))
        await client.add_cog(f.Say(client))
        await client.add_cog(f.Cat(client))
        await client.add_cog(ps.PunishmentSystem(client))
        await client.add_cog(ps.ExpiredPunishmentManager(client))
        await client.add_cog(pc.PunishmentCommands(client))
        await client.add_cog(pcc.PunishmentCaseCommands(client))
        await client.add_cog(sn.StaffNotes(client))
        await client.add_cog(u.SQLQuery(client))
    else:
        # Debug Modules / Cogs
        pass



# Initialize cogs
asyncio.run(init_cogs())

# Run bot
client.run(asyncio.run(getToken()))

#FIX #
##async def on_ready():
    ##base.BaseModule.bot_started = True``
    ##print("Bot active!")

# Ensure cogs are loaded before calling main on_ready listener
##@client.before_invoke
##async def wait_for_cogs():
    ##await client.wait_until_ready()