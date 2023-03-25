import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

class VC(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self._last_member = None
		

