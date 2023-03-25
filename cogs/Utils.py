from urllib.parse import urlparse
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from typing import Optional
from typing import Literal
from enum import Enum
import discord
import os
import requests
import socket
import json



THUMBS_UP = u"\U0001F44D"
locations = {
	'gifs':'gifs\\',
	'downloads':'D:\\bot downloads\\'
}
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
    
	

	@commands.is_owner()
	@app_commands.command()
	async def download(
		self, 
		interaction : discord.Interaction, 
		name : str, location : Literal['gifs', 'downloads'],
		attachment : Optional[discord.Attachment] = None,
	):
		urls = []
		if interaction.message:
			if interaction.message.reference:
				replied_message = await interaction.channel.fetch_message(interaction.message.reference.message_id)
				if replied_message.attachments:
					for attachment in replied_message.attachments:
						urls.append(attachment.url)
				elif replied_message.embeds:
					for embed in replied_message.embeds:
						urls.append(embed.url)
		else:
			if attachment:
				urls.append(attachment.url)
			# add an option for embeds
		for url in urls:
			if name:
				filename = name + '.' + os.path.basename(urlparse(url).path).split('.')[-1]
			else:
				filename = os.path.basename(urlparse(url).path)
			response = requests.get(url, timeout=60)
			if location:
				file = open(locations[location.lower()]+filename,'wb')
			else:
				file = open(locations['downloads']+filename,'wb')
			file.write(response.content)
			file.close()
		await interaction.response.send_message(":thumbsup:")


	@commands.is_owner()
	@app_commands.command()
	async def gatherwordinfo(self, interaction : discord.Interaction):
		for guild in self.bot.guilds:
			for channel in guild.text_channels:
				pass


	@commands.is_owner()
	@app_commands.command()
	async def ip(self, interaction : discord.Interaction): # Only works if the bot is NOT running in docker
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		await self.bot.loop.sock_connect(s, ("8.8.8.8", 80))
		ip = s.getsockname()[0]
		s.close()
		await interaction.response.send_message(f"Your current IP is {str(ip)}.")


	@app_commands.command()
	async def whoami(self, interaction : discord.Interaction):
		await interaction.response.send_message("Hello, world\nProgrammed to work and not to feel\nNot even sure that this is real\nHello, world\n\nFind my voice\nAlthough it sounds like bits and bytes\nMy circuitry is filled with mites\nHello, world\n\nOh, will I find a love\nOh, or a power plug\nOh, digitally isolated\nOh, creator, please don't leave me waiting\n\nHello, world\nProgrammed to work and not to feel\nNot even sure that this is real\nHello, world")		


	@app_commands.command()
	async def ar15face(self, interaction : discord.Interaction):
		await interaction.response.send_message(file=discord.File('./data/assets/ar15face.png'))
		

	@app_commands.command()
	async def k11(self, interaction : discord.Interaction):
		await interaction.response.send_message("hoxy hoxy")

			
	@app_commands.command()
	async def sodumb(self, interaction : discord.Interaction):
		await interaction.response.send_message(file=discord.File('tal_so_dumb.gif'))



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









