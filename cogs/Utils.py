import discord
from discord import app_commands
from discord.ext import commands


from typing import Optional
from typing import Literal
from enum import Enum

from datetime import datetime
from urllib.parse import urlparse

import os
import json
import requests




LOG_PATH = '../data/logs/'




class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None


    @app_commands.command()
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!")
        await log(f"Pinged by { interaction.user }")



# To be used by all other cogs
async def log(Text : str) -> None:
    Time = datetime.now().strftime("%Y/%m/%d - %H:%M")
    LogMessage = f"[{ Time }] : { Text }"

    print(LogMessage)

    with open(LOG_PATH + 'log.txt','r') as f:
        log_data = f.read()

    with open(LOG_PATH + 'log.txt','w+') as f:
        f.write(log_data + LogMessage + "\n")

