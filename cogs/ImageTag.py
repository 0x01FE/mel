import discord
from discord import app_commands
from discord.ext import commands

from urllib.parse import urlparse

import os
import json
import requests


TAG_DATA_PATH = '../data/tagged_images/'


class ImageTag(commands.GroupCog, name="tag"):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        super().__init__()



    @app_commands.command(name="create")
    async def tagCreate(self,
        interaction : discord.Interaction,
        tagname : str,
        attachment : discord.Attachment
    ):
        with open(f'{ TAG_DATA_PATH }tags.json', 'r+') as f:
            tag_index = json.loads(f.read())

        if not tagname in tag_index:
            filename = str(tag_index["last"] + 1)
            url = attachment.url
            ext = '.' + os.path.basename(urlparse(url).path).split('.')[-1]

            tag_index["images"][tagname] = filename + ext
            tag_index["last"] = tag_index["last"] + 1

            response = requests.get(url, timeout=60)

            # Save the image
            with open(f"{ TAG_DATA_PATH }{ filename }{ ext }", 'wb') as f:
                f.write(response.content)

            # Save the associated tag data
            with open(f'{ TAG_DATA_PATH }tags.json', 'w+') as f:
                f.write(json.dumps(tag_index))

            await interaction.response.send_message(f"Tag { tagname } created!")
        else:
            await interaction.response.send_message(f"Sorry, \"{ tagname }\" already exists as a tag.")



    @app_commands.command(name='get')
    async def tagGet(self,
        interaction: discord.Interaction,
        tagname : str
    ):
        with open(f'{ TAG_DATA_PATH }tags.json', 'r+') as f:
            tag_index = json.loads(f.read())

        if tagname in tag_index['images']:
            await interaction.response.send_message(file=discord.File(TAG_DATA_PATH + tag_index['images'][tagname]))
        else:
            await interaction.response.send_message(f'{ tagname } tag was not found.')



    @app_commands.command(name='delete')
    async def tagDelete(self,
        interaction : discord.Interaction,
        tagname : str
    ):
        with open(f'{ TAG_DATA_PATH }tags.json', 'r+') as f:
            tag_index = json.loads(f.read())

        if tagname in tag_index['images']:
            os.remove(TAG_DATA_PATH + tag_index['images'][tagname])
            del tag_index['images'][tagname]

            with open(f'{ TAG_DATA_PATH }tags.json', 'w+') as f:
                f.write(json.dumps(tag_index))

        await interaction.response.send_message(f"{ tagname } tag was deleted.")



    @app_commands.command(name='list')
    async def tagList(self,
        interaction : discord.Interaction
    ):
        with open(f'{ TAG_DATA_PATH }tags.json', 'r+') as f:
            tag_index = json.loads(f.read())

        response = ''

        for tag in tag_index['images']:
            response += tag + '\n'

        await interaction.response.send_message(response, ephemeral=True)


