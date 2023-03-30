import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

import os
import asyncio

thumbs_up = u"\U0001F44D"
FFMPEG_PATH = ''


class VC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
		
    @commands.command()
    async def play(self, ctx : commands.Context, url : str):
        message = ctx.message

        if message.author.voice: ## check if in vc
            if self.bot.user not in message.author.voice.channel.members: # check if client already open in that vc
                await message.author.voice.channel.connect()

            # actual stuff

            tasks = []
            tasks.append(self.bot.loop.run_in_executor(None, download_spfy_song, url)) # run download in another thread
            await asyncio.wait(tasks)
            await message.channel.guild.change_voice_state(channel=message.author.voice.channel, self_deaf=True)
            message.channel.guild.voice_client.play(discord.FFmpegPCMAudio(source='temp.mp3'))

        else:
            await message.reply("User is not in a voice channel.")


    def download_spfy_song(self, song_url): # goes with VC stuff if you make the music stuff apart of VC
        os.system(f'cmd /c py -m zotify --output temp.ogg {song_url}')



    @commands.command()
    async def leave(self, ctx : commands.Context):
        if ctx.message.author.voice.channel and bot.user in ctx.message.author.voice.channel.members:
            await ctx.message.channel.guild.voice_client.disconnect()
            await ctx.message.add_reaction(thumbs_up)
        else:
            await ctx.message.reply('User is not in voice channel.')


