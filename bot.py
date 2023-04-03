import discord
from discord import app_commands
from discord.ext import commands, tasks

from socket import TIPC_WITHDRAWN
import aiohttp, asyncio, requests, os, pyttsx3, tweepy, wget, math, glob, json, yaml
from urllib.parse import urlparse
from datetime import datetime
from bs4 import BeautifulSoup as _soup
from PIL import Image
import os
#from fpdf import FPDF

from multiprocessing import Process
from moviepy.editor import VideoFileClip
from typing import Optional


from random import randint

# COGS
from cogs import Utils
from cogs import ImageEdit
from cogs import SpotifyUtils
from cogs import Help
from cogs import Leaderboard
from cogs import Misc


AR15FACE_FILE_PATH = 'data/assets/ar15face.png'
TAL_FILE_PATH = 'data/assets/tal_so_dumb.gif'
locations = {'gifs':'gifs\\','downloads':'D:\\bot downloads\\'}

engine = pyttsx3.init()
voices = engine.getProperty('voices')


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix = "-", intents = intents)

STATUS_LIST_PATH = 'data/assets/status-list.json'
CONFIG_PATH = 'cogs/config.yml'
ODEN_PATH = 'data/assets/oden.json'


vc = None
pic_ext = ['.jpg','.png','.jpeg','.webp']


# Reading the config here and in the setup hook, can probably knock it down to one read
with open(CONFIG_PATH, 'r') as f:
	config = yaml.safe_load(f)


token = config['bot']['token']




@bot.event
async def setup_hook():
	global other_channels
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')

	bot.first_ready = True
	


	# CONFIG 
	with open(CONFIG_PATH,'r') as f:
		bot.config = yaml.safe_load(f)

	for value in bot.config['bot']['spotify']:
		os.system(f"export {value}='{bot.config['bot']['spotify'][value]}'")
		print(f'{value} set!')

	bot.tenor_base_url = 'https://g.tenor.com/v1/gifs?ids={}&key=' + bot.config['bot']['tenor']['api_key']


	# Load All Cogs
	await bot.add_cog(Utils.Utils(bot))
	await Misc.log("Cog Loaded: Utils")

	await bot.add_cog(SpotifyUtils.SpotifyUtils(bot))
	await Misc.log("Cog Loaded: SpotifyUtils")

	await bot.add_cog(Help.Help(bot))
	await Misc.log("Cog Loaded: Help")

	await bot.add_cog(Leaderboard.Leaderboard(bot))
	await Misc.log("Cog Loaded: Leaderboard")

	await bot.add_cog(Misc.Misc(bot))
	await Misc.log("Cog Loaded: Misc")


	if not bot.config['bot']['server']:
		owner_response = input("Boot with ImageEdit (Y/N)? ").lower()
	else:
		owner_response = "y"

	if owner_response == "y":
		await bot.add_cog(ImageEdit.ImageEdit(bot))
		await Misc.log("Cog Loaded: ImageEdit")

	##vc_check.start()
	status_change.start()
	await Misc.log("Bot Pre-Initialized")
		

@bot.event
async def on_ready():
	# Load all app_commands for all guilds

	if bot.first_ready:

		for guild in bot.guilds:
			guild_obj = discord.Object(id=guild.id)
			bot.tree.copy_global_to(guild=guild_obj)
			await bot.tree.sync(guild=guild_obj)
			await Misc.log(f"Commands synced in : {guild.name}")

		await Misc.log("Bot Initialized")
		bot.first_ready = False
		


# Error Logging
@bot.event
async def on_error(e):
	await Misc.log(f'Error : {e}')


## utility
		
@bot.command()
async def set(ctx, *args):
	if len(args) == 0:
		embed = await help_set_embed(ctx.me.colour)
		await ctx.send(embed=embed)
	elif len(args) == 1:
		if args[0] == 'tts':
			embed = await help_tts_embed(ctx.me.colour)
			await ctx.send(embed=embed)
		else:
			await ctx.send('Please refer to `-set`')
	elif len(args) == 2:
		if args[0] == 'tts':
			if args[1] == 'speed':
				await ctx.send("Missing argument (Speed int)")
			elif args[1] == 'voice':
				await ctx.send("Missing argument (Voice name)")
			else:
				await ctx.send("Please refer to `-set tts`")
	elif len(args) == 3:
		if args[0].lower() == 'tts':
			if args[1].lower() == 'speed':
				if args[2].isdecimal():
					if int(args[2]) >= 100 and  int(args[2]) <= 300:
						engine.setProperty('rate',int(args[2]))
						await ctx.send("Successfully set speed to " +args[2]+ ".")
			if args[1].lower() == 'voice':
				if args[2].lower() == 'tim':
					engine.setProperty('voice',voices[0].id)
					await ctx.send("Successfully set voice to Tim.")
				elif args[2].lower() == 'alice':
					engine.setProperty('voice',voices[1].id)
					await ctx.send("Successfully set voice to Alice.")




## event catchers

@bot.event
async def on_message(message : discord.Message):
    global vc

    with open(ODEN_PATH, 'r') as f:
        words = json.loads(f.read())['words']

    MessageWords = message.content.lower().split(' ')

    for word in words:
        if word.split(' ') in MessageWords:
            if message.author.name == '3rror8' and message.author.discriminator == '6155':
                await message.channel.send(file=discord.File(AR15FACE_FILE_PATH))
                break

    if message.content:
        if "so dumb" in message.content.lower():
            Chance = randint(1,5)
            if Chance == 1:
                await message.channel.send(file=discord.File(TAL_FILE_PATH))

        if message.content[0] == "'": ## TEXT TO SPEECH
            if message.author.voice:
                if bot.user not in message.author.voice.channel.members:
                    await message.author.voice.channel.connect()
                if message.author.name == 'chicken little' and message.author.discriminator == '2608' and 'get real' in message.content:
                    await message.channel.send('YOU are not allowed to say that.')
                elif message.content == "'leave":
                    if message.author.voice.channel and bot.user in message.author.voice.channel.members:
                        await message.channel.guild.voice_client.disconnect()
                else:
                    await message.channel.guild.change_voice_state(channel=message.author.voice.channel, self_deaf=True)
                    engine.save_to_file(message.content[1:], 'audio.mp3')
                    engine.runAndWait()
                    message.channel.guild.voice_client.play(discord.FFmpegPCMAudio(source="audio.mp3"))
            else:
                await message.reply("User is not in a voice channel.")
        elif message.content[:2] == '--':
            pass
        else:
            await bot.process_commands(message)
    else:
        await bot.process_commands(message)





## HELP EMBED BUILDERS {this 100% needs to go with the VC stuff}

async def help_tts_embed(embed_colour):
    embed = discord.Embed(title = "TTS Help Menu", description = 'Welcome to the TTS help menu.', colour = embed_colour)
    embed.set_footer(text='Bot developed by 0x01FE#1244')
    embed.add_field(name='-set tts', value='> Brings up this help menu.\nValues:\n  <+> speed\n  > Default is 200 words per minute. Can range from 100-300 words per minute.\n  <+> voice\n  > Two available voices include Tim and Alice. ',inline=False)
    return embed

async def help_set_embed(embed_colour):
    embed = discord.Embed(title = "Set Help Menu", description = 'Welcome to the set help menu.', colour = embed_colour)
    embed.set_footer(text='Bot developed by 0x01FE#1244.')
    embed.add_field(name='-set tts', value='> Brings up this help menu.\nValues:\n  <+> speed\n  > Default is 200 words per minute. Can range from 100-300 words per minute.\n  <+> voice\n  > Two available voices include Tim and Alice. ',inline=False)
    return embed









# tasks
'''
@tasks.loop(seconds=10,count=None)
async def vc_check():
    for voice_client in bot.voice_clients:
        if len(voice_client.channel.members) == 1:
            await voice_client.disconnect()

@vc_check.before_loop
async def before_vc_check():
    await bot.wait_until_ready()
'''	



@tasks.loop(minutes=15.0,count=None)
async def status_change():

    with open(STATUS_LIST_PATH, "r") as f:
        status_list = json.load(f)

    Chance = randint(1,2)

    if Chance == 1:
        Chance = randint(0,len(status_list['Listening'])-1)
        await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=status_list['Listening'][Chance]))

    elif Chance == 2:
        Chance = randint(0,len(status_list['Playing'])-1)
        await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name=status_list['Playing'][Chance]))

'''
Explanation of why it must wait until the bot is ready.
Bot cannot make api calls before it is "ready" and it is not "ready" in the setup hook where the loop is started.
The task loop is not started in on_ready because on ready can run at anytime.
'''
@status_change.before_loop
async def before_status_change():
    await bot.wait_until_ready()




bot.run(token)
