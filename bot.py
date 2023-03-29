import discord
from discord import app_commands
from discord.ext import commands, tasks

from socket import TIPC_WITHDRAWN
import aiohttp, asyncio, requests, os, pyttsx3, dice_master as dice, tweepy, wget, math, glob, json, yaml
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




locations = {'gifs':'gifs\\','downloads':'D:\\bot downloads\\'}


rewind = '\u23EA'
arrow_left = '\u2B05'
arrow_right = '\u27A1'
fast_forward = '\u23E9'
thumbs_up = u"\U0001F44D"
x_emoji = '\u274C'
active_viewers = {} ## by message id
bot_author = '0x01FE#1244'
engine = pyttsx3.init()
voices = engine.getProperty('voices')


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix = "-", intents = intents)

STATUS_LIST_PATH = 'data/assets/status-list.json'
CONFIG_PATH = 'cogs/config.yml'


guns_channel = None
vc = None
pic_ext = ['.jpg','.png','.jpeg','.webp']


# Reading the config here and in the setup hook, can probably knock it down to one read
with open(CONFIG_PATH, 'r') as f:
	config = yaml.safe_load(f)

token = config['bot']['token']





## basic commands



@bot.event
async def setup_hook():
	global other_channels
	global emperor
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
		print("["+str(datetime.now().strftime("%H:%M"))+f"] : Cogs Loaded: ImageEdit")

	##vc_check.start()
	status_change.start()
	emperor = await bot.fetch_user(516017792739311636) # Me
	print("["+str(datetime.now().strftime("%H:%M"))+"] : Bot Pre-Initialized")
		

@bot.event
async def on_ready():
	# Load all app_commands for all guilds

	if bot.first_ready:
		for guild in bot.guilds:
			print("["+str(datetime.now().strftime("%H:%M"))+f"] : Commands added to : {guild.name}")
			guild_obj = discord.Object(id=guild.id)
			bot.tree.copy_global_to(guild=guild_obj)
			await bot.tree.sync(guild=guild_obj)
			other_channels = {}
		print("["+str(datetime.now().strftime("%H:%M"))+"] : Bot Initialized")
		bot.first_ready = False
		




## utility


								
			
@bot.command()
async def gif_archive(ctx): # TODO: FIX THIS, tenor_apikey is from old config
	if str(ctx.message.author) == bot_author:
		gif_list = glob.glob('gifs')
		async with ctx.typing():
			history = await ctx.message.channel.history(limit=None).flatten()
			for message in history:
				if message.embeds:
					for embed in message.embeds:
						if (str(message.id) + '.gif') not in gif_list:
							if 'tenor' in embed.url:
								tenor_id = embed.url.split('-')[-1]
								response = json.loads(requests.get(bot.tenor_base_url.format(tenor_id, tenor_apikey), timeout=60).content)
								try:
									response = requests.get(response['results'][0]['media'][0]['gif']['url'],timeout=60)
									file = open('gifs/'+str(message.id)+'.gif', "wb")
									file.write(response.content)
									file.close()
								except:
									print(response)
							else:
								try:
									response = requests.get(embed.url, timeout=60)
									file = open('gifs/'+str(message.id)+'.gif', "wb")
									file.write(response.content)
									file.close()
								except:
									print('Failed gif download\nLink: '+embed.url+'\n')
		await ctx.send('Done.')

@bot.command()
async def dicer(ctx):		
	if ctx.message.attachments:
		response = requests.get(ctx.message.attachments[0].url)
	elif ctx.message.embeds:
		response = requests.get(ctx.message.embeds[0].url)
	file = open("soon_to_be_dice.png", "wb")
	file.write(response.content)
	file.close()
	async with ctx.typing():
		try:
			dice.convert_dice('soon_to_be_dice.png')
		except:
			await ctx.send("@MisterUnknown#1244 your stupid bot is broken again")
		try:
			await ctx.send(file=discord.File('soon_to_be_dice_dice.png'))
		except:
			await ctx.send("The file was to big to send")	

@bot.command()
async def leave(ctx):
	if ctx.message.author.voice.channel and bot.user in ctx.message.author.voice.channel.members:
		await ctx.message.channel.guild.voice_client.disconnect()	
		await ctx.message.add_reaction(thumbs_up)
	else:
		await ctx.message.reply('User is not in voice channel.')	
		
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
async def on_message(message):
	global vc
	trigger = False
	trigger_words = ['odor','feet','stink','lick','sweat','soles','smell','toes','sniff','socks','stench','musk','reek','feets','stinky','reeks','licking','licks','sweaty','sole','smelly','rogue lineage','toe','sock']
	for word in trigger_words:
		for message_word in message.content.lower().split(' '):
			ans = ''
			for char in message_word:
				if char.isalpha():
					ans+=char
			if word.lower() == ans:
				if message.author.name == '3rror8' and message.author.discriminator == '6155':
					await message.channel.send(file=discord.File('ar15face.png'))
					trigger = True
					break
		if trigger:
			break
	if message.content:
		if "so dumb" in message.content.lower():
			Chance = random.randint(1,20)
			if Chance == 1:
				await message.channel.send(file=discord.File('tal_so_dumb.gif'))

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
					message.channel.guild.voice_client.play(discord.FFmpegPCMAudio(executable="D:/ffmpeg-20200831-4a11a6f-win64-static/bin/ffmpeg.exe", source="audio.mp3"))
			else:
				await message.reply("User is not in a voice channel.")
		elif message.content[:2] == '--':
			pass
		else:
			await bot.process_commands(message)
	else:
		await bot.process_commands(message)
		
@bot.event
async def on_reaction_add(reaction, user):
	global active_viewers
	if reaction.message.id in active_viewers:
		message = active_viewers[reaction.message.id][0]
		author = active_viewers[reaction.message.id][1]
		place = active_viewers[reaction.message.id][2]
		image_links = active_viewers[reaction.message.id][3]
		if user == author:
			if reaction.emoji == rewind:
				if place-5 > 0:
					embed = message.embeds[0]
					place-=5
					embed.set_image(url=image_links[place][0])
					await message.edit(embed=embed)
					await reaction.remove(author)
			elif reaction.emoji == arrow_left:
				if place-1 >= 0:
					embed = message.embeds[0]
					place-=1
					embed.set_image(url=image_links[place][0])
					await message.edit(embed=embed)
					await reaction.remove(author)
			elif reaction.emoji == arrow_right:
				if place+1 <= len(image_links):
					embed = message.embeds[0]
					place+=1
					embed.set_image(url=image_links[place][0])
					await message.edit(embed=embed)
					await reaction.remove(author)
			elif reaction.emoji == fast_forward:
				if place+5 <= len(image_links):
					embed = message.embeds[0]
					place+=5
					embed.set_image(url=image_links[place][0])
					await message.edit(embed=embed)
					await reaction.remove(author)
			elif reaction.emoji == x_emoji:
				perms = user.permissions_in(reaction.message.channel)
				if perms.manage_messages:
					temp = await reaction.message.channel.fetch_message(image_links[place][1])
					print(temp.content)
				await temp.delete()
				await reaction.remove(author)
		active_viewers[reaction.message.id] = (message,author,place,image_links)
			

# Work In Progress
@bot.command()
async def play(ctx, url):
	message = ctx.message
	if message.author.voice: ## check if in vc
		if bot.user not in message.author.voice.channel.members: ## check if client already open in that vc
			await message.author.voice.channel.connect()
		## actual stuff
		tasks = []
		tasks.append(bot.loop.run_in_executor(None, download_spfy_song, url)) ## run download in another thread
		await asyncio.wait(tasks)
		await message.channel.guild.change_voice_state(channel=message.author.voice.channel, self_deaf=True)
		message.channel.guild.voice_client.play(discord.FFmpegPCMAudio(executable="D:/ffmpeg-20200831-4a11a6f-win64-static/bin/ffmpeg.exe", source='temp.mp3'))
	else:
		await message.reply("User is not in a voice channel.")
	

	
	
	
	
		
## general methods (will need to go with their respective commands)

def res_up_local(filename): # goes with res_up
	scale, noise = 2, 3
	os.system("cmd /c waifu2x-converter-cpp -c 9 -q 101 --scale-ratio "+str(scale)+" --noise-level "+str(noise)+" -m noise-scale -i "+filename)

def res_queue(item): # goes with res_up? i don't know if i still use this actually
	os.system("cmd /c waifu2x-converter-cpp -c 9 -q 101 --scale-ratio "+item[1][1]+" --noise-level "+item[1][0]+" -m noise-scale -i "+item[0])	
	
def download_spfy_song(song_url): # goes with VC stuff if you make the music stuff apart of VC
	os.system(f'cmd /c py -m zotify --output temp.ogg {song_url}')
	


async def cmd_log_add(cmd,user,time): # only used for a twitter command i think
	log_data = None
	with open('log.txt','r') as f:
		log_data = f.read()
	with open('log.txt','w+') as f:
		f.write(log_data + '\n' + cmd+' by: '+str(user)+' at '+str(time))






## HELP EMBED BUILDERS {this 100% needs to go with the VC stuff}

async def help_tts_embed(embed_colour):
	embed = discord.Embed(title = "TTS Help Menu", description = 'Welcome to the TTS help menu.', colour = embed_colour)
	embed.set_footer(text='Bot developed by '+bot_author+".")
	embed.add_field(name='-set tts', value='> Brings up this help menu.\nValues:\n  <+> speed\n  > Default is 200 words per minute. Can range from 100-300 words per minute.\n  <+> voice\n  > Two available voices include Tim and Alice. ',inline=False)
	return embed
	
async def help_set_embed(embed_colour):
	embed = discord.Embed(title = "Set Help Menu", description = 'Welcome to the set help menu.', colour = embed_colour)
	embed.set_footer(text='Bot developed by '+bot_author+".")
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
