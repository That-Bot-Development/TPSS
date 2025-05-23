import discord
from discord import app_commands

from modules.base import BaseModule
from modules.util.embed_maker import *

import requests
import time


class Say(BaseModule):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="say", description="Put words in That Bot's figurative mouth.")
    @app_commands.describe(message="The message to have the bot send.",replyto="The Message ID of the message the bot will respond to.")
    async def say(self, interactions: discord.Interaction, message:str, replyto:str=None):

        try:
            if replyto == None:
                response = await interactions.channel.send(message)
            else:
                response = await interactions.channel.fetch_message(replyto)
                await response.reply(message)
            await self.d_consts.CHANNEL_MISCLOGS.send(embed=EmbedMaker(
                embed_type=EmbedType.ACTIVITY_LOG,
                title = "Say Command",
                message=f"**{interactions.user.display_name}:** {message} ({response.jump_url})"
            ).create(),silent=True,allowed_mentions=self.d_consts.VAR_ALLOWEDMENTIONS_NONE)
            await interactions.response.send_message("<:Advertisement:622603404212174849>",ephemeral=True,delete_after=0)

        except Exception as e:
            print(f"Exception occured in 'say' operation: {e}")
            await interactions.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.MISC,
                message="This likely means That Bot does not have access to speak in this channel.\n\nContact an Admin if you believe this is a mistake.",
                error=True
            ).create(),ephemeral=True,delete_after=20)

class Cat(BaseModule):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="cat", description="Provides cat.")
    @app_commands.describe(filter="Filter what type of cat you would like provided.")
    async def cat(self, interaction: discord.Interaction, filter:str=None):
        await interaction.response.defer()

        try:
            if filter == None:
                response = requests.get(f"https://cataas.com/cat?{int(time.time())}")
            else:
                response = requests.get(f"https://cataas.com/cat/{filter}?{int(time.time())}")
            if response.status_code == 200:
                 # Get the content type (e.g., image/jpeg, image/png)
                content_type = response.headers.get('Content-Type')

                # Extract the image extension from the content type
                if content_type:
                    ext = content_type.split('/')[-1]  # Get the file extension (e.g., jpeg, png, gif)
                else:
                    ext = "bin"  # If content type isn't available, use a generic extension
                
                with open(f"cat.{ext}", "wb") as file:
                    # Write the image content to the file
                    file.write(response.content)

                with open(f"cat.{ext}", "rb") as file:
                    dFile = discord.File(file,filename=f"cat.{ext}")
                    
                embed = discord.Embed(title="")
                embed.set_footer(text="From CatAAS")
                embed.set_image(url=f"attachment://cat.{ext}")  # Use the URL from the response
                #TODO: Replace with EmbedMaker
                await interaction.followup.send(file=dFile,embed=embed)
            else:
                raise Exception(f"Encountered code {response.status_code}")

        except Exception as e:
            print(f"Exception occured in 'cat' operation: {e}")
            await interaction.response.send_message(embed=EmbedMaker(
                embed_type=EmbedType.MISC,
                message="This likely means the [CatAAS API](https://cataas.com/) is down.\n\nContact an Admin if you believe this is a mistake.",
                error=True
            ).create(),ephemeral=True) # FIXME: This is inconsistent! Other error messages can delete after 20s, cannot due to deferring...
        
