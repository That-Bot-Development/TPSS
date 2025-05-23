import discord
from discord.ext import commands

from modules.base import BaseModule

from modules.util.embed_maker import *

# DEPRECATED AS OF 2.8.0
class BanDM(BaseModule):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if message.channel.id == 578725402638286879 and ".ban" in message.content and not message.author.bot:
            user = self.client.get_user(int(message.content[5:23]))

            embed = discord.Embed(colour = discord.Colour(0x69B2FF))
            embed.set_thumbnail(url=message.guild.icon)
            embed.set_author(name=user.name, icon_url=user.avatar)
            embed.add_field(name="You have been banned from That Place.", value="If you feel as if your punishment should be removed, please fill out [this](https://forms.gle/ewMRCRny6RQMZxna9) form. Be reasonable when submitting your appeal.", inline=False)
            embed.set_footer(text="Punishment Notice")
            await user.send(content=None, embed=embed)

        # DEPRECATION ALERT
        elif ".punishments" in message.content and not message.author.bot:
            await message.channel.send(embed=EmbedMaker(embed_type=EmbedType.MISC,title="<:alert:1346654360012329044> Deprecated command!",message="`.punishments` is no longer updated with the most recent punishment logs and will soon be retired.\nPlease use `/punishments` instead!").create())