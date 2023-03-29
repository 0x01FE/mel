from datetime import datetime
from discord import app_commands
from discord.ext import commands
from typing import Optional
from typing import Literal
from enum import Enum
import discord
import os
import json



LOG_PATH = '../data/logs/'
TAG_DATA_PATH = '../data/tagged_images/'

class TagCMDS(Enum):
	create = 1
	get = 2
	delete = 3
	list = 4

class Utils(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self._last_member = None


	@app_commands.command()
	async def ping(self, interaction: discord.Interaction):
		await interaction.response.send_message("Pong!")
		print("["+str(datetime.now().strftime("%H:%M"))+"] : pinged")


	@app_commands.command()
	async def tag(self,
		interaction : discord.Interaction,
		command : Literal['create','get','delete','list'],
		tagname : Optional[str] = None,
		attachment : Optional[discord.Attachment] = None
	):
		if TagCMDS[command].value == 1:
				if tagname != None and attachment != None:
					await self.tagcreate(tagname, attachment, interaction)
				else:
					await interaction.response.send_message("Command tag requires a tag name and attachement.")
		elif TagCMDS[command].value == 2:
			if tagname != None:
				await self.gettag(tagname, interaction)
			else:
				await interaction.response.send_message("Command requires a tagname")
		elif TagCMDS[command].value == 3:
			if tagname != None:
				await self.deletetag(tagname, interaction)
			else:
				await interaction.response.send_message("Command requires a tagname")
		elif TagCMDS[command].value == 4:
			await self.listtags(interaction)




	async def tagcreate(self, name, attachment : discord.Attachment, interaction : discord.Interaction):
		with open(TAG_DATA_PATH + 'tags.json', 'r+') as f:
			tag_index = json.loads(f.read())

		if not name in tag_index:
			filename = str(tag_index["last"] + 1)
			url = attachment.url
			ext = '.' + os.path.basename(urlparse(url).path).split('.')[-1]


			tag_index["images"][name] = filename + ext
			tag_index["last"] = tag_index["last"] + 1

			response = requests.get(url, timeout=60)
			file = open(TAG_DATA_PATH + filename + ext,'wb')
			file.write(response.content)
			file.close()

			with open(TAG_DATA_PATH + 'tags.json', 'w+') as f:
				f.write(json.dumps(tag_index))

			await interaction.response.send_message(f"Tag {name} created!")
		else:
			await interaction.response.send_message(f"Sorry, \"{name}\" already exists as a tag.")


	async def gettag(self, name, interaction : discord.Interaction):
		with open(TAG_DATA_PATH + 'tags.json', 'r+') as f:
			tag_index = json.loads(f.read())

		if name in tag_index['images']:
			await interaction.response.send_message(file=discord.File(TAG_DATA_PATH + tag_index['images'][name]))
		else:
			await interaction.response.send_message(f'{name} tag was not found.')


	async def deletetag(self, name, interaction : discord.Interaction):
		with open(TAG_DATA_PATH + 'tags.json', 'r+') as f:
			tag_index = json.loads(f.read())

		if name in tag_index['images']:
			os.remove(TAG_DATA_PATH + tag_index['images'][name])
			del tag_index['images'][name]

			with open(TAG_DATA_PATH + 'tags.json', 'w+') as f:
				f.write(json.dumps(tag_index))

		await interaction.response.send_message(f"{name} tag was deleted.")


	async def listtags(self, interaction : discord.Interaction):
		with open(TAG_DATA_PATH + 'tags.json', 'r+') as f:
			tag_index = json.loads(f.read())

		response = ''

		for tag in tag_index['images']:
			response += tag + '\n'

		await interaction.response.send_message(response)



# To be used by all other cogs
async def log(Text : str):
    LogMessage = f"[{ datetime.now().strftime("%H:%M") }] : { Text }"

    print(LogMessage)

    with open(LOG_PATH + 'log.txt','r') as f:
        log_data = f.read()

    with open(LOG_PATH + 'log.txt','w+') as f:
        f.write(log_data + LogMessage + "\n")

