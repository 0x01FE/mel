import discord, asyncio, requests, wget, os, math, yaml, tweepy
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from datetime import datetime
#import torch
#from diffusers import StableDiffusionPipeline, DDIMScheduler
from typing import Optional, Literal
from moviepy.editor import VideoFileClip
from urllib.parse import urlparse

#device = "cuda"
#MY_TOKEN = "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" # load this from a file later

CONFIG_PATH = 'cogs/config.yml'

from .Misc import log


class ImageEdit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self.tasks = []




        consumer_key = self.bot.config['bot']['twitter']['consumer_key']
        consumer_secret = self.bot.config['bot']['twitter']['consumer_secret']
        access_token = self.bot.config['bot']['twitter']['access_token']
        access_token_secret = self.bot.config['bot']['twitter']['access_secret']

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth,wait_on_rate_limit=True)

        ''' Turned off for server
        self.models = {}

        temp = [("SD", "CompVis/stable-diffusion-v1-4"), ("WD", "hakurei/waifu-diffusion")] # Stable Diffusion, Waifu Diffusion
        for model, model_id in temp:
                if model_id == "CompVis/stable-diffusion-v1-4":
                    self.models[model] = StableDiffusionPipeline.from_pretrained(
                        model_id,
                        torch_dtype=torch.float16,
                        revision="fp16",
                        use_auth_token=MY_TOKEN,
                        scheduler=DDIMScheduler(
                            beta_start=0.00085,
                            beta_end=0.012,
                            beta_schedule="scaled_linear",
                            clip_sample=False,
                            set_alpha_to_one=False,
                        ),
                    )
                else:
                    self.models[model] = StableDiffusionPipeline.from_pretrained(
                        model_id,
                        torch_dtype=torch.float16,
                    ).to('cuda')
                self.models[model] = self.models[model].to(device)
                self.models[model].safety_checker = self.dummy





    def dummy(self, images, **kwargs):
        return images, False




    @app_commands.command()
    async def txt2img(
        self,
        interaction : discord.Interaction,
        prompt : str,
        model : Optional[Literal["Stable Diffusion","Waifu Diffusion"]]
    ):
        # convert from user friendly text to jackson text
        if model:
            if model == "Stable Diffusion":
                model = "SD"
            elif model == "Waifu Diffusion":
                model = "WD"
        else:
            model = "SD" # if model not specified use Stable Diffusion

        if not self.tasks: # The entire self.tasks list is to A) use asyncio.wait which needs a list of running tasks B) to keep SOME people from overloading the bot with prompts
            await interaction.response.defer()
            self.tasks.append(([(self.bot.loop.run_in_executor(None, self.txt2imgtask, prompt, model))], interaction.user))
            async with interaction.channel.typing():
                await asyncio.wait(self.tasks[0][0])
                await interaction.followup.send(content='Command requested by '+str(interaction.user)+'.', file=discord.File(prompt+".png"))
                os.remove(prompt+".png")
                self.tasks = []
        else:
            await interaction.response.send_message("Sorry, "+str(self.tasks[0][1])+" is running a prompt right now.")


    def txt2imgtask(self,prompt,model):
        with torch.autocast("cuda"):
            image = self.models[model](prompt, guidance_scale=7.5)["sample"][0]
        image.save(prompt+".png")

'''

    @commands.command()
    async def twitter(self, ctx, *args):
        await log(f'{ctx.message.content} by {ctx.message.author}')
        other_channels = {}
        other_server = self.bot.get_guild(883156816249368576)
        other_channels['other'] = other_server.get_channel(883157788421935136)
        other_channels['fate'] = other_server.get_channel(883201954715697242)
        other_channels['touhou'] = other_server.get_channel(883395217414291456)
        other_channels['tower-defense-girls'] = other_server.get_channel(883202503888490528)
        other_channels['guns'] = other_server.get_channel(883574520882012170)
        extract_numbers = []
        tags = []
        trigger = False
        embed_colour = ctx.me.colour
        resup = False
        sync = False
        spoiler_tag = False
        if len(args) > 1:
            if 'res_up' in args:
                resup = True
            if 'spoiler' in args or 'sp' in args:
                spoiler_tag = True
            if 'sync' in args:
                sync = True
            for arg in args:
                if '[' in arg and ']' in arg:
                    extract_temp = arg.split(',')
                    for num in extract_temp:
                        num = num.replace('[','')
                        num = num.replace(']','')
                        extract_numbers.append(int(num))
                elif 'tags{' in arg or '{' in arg and '}' in arg:
                    extract_temp = arg.split(',')
                    for num in extract_temp:
                        num = num.replace('tags{','')
                        num = num.replace('{','')
                        num = num.replace('}','')
                        tags.append(num)
        if ctx.message.reference:
            if len (args) > 0:
                if 'res_up' in args:
                    resup = True
                if 'spoiler' in args or 'sp' in args:
                    spoiler_tag = True
                for arg in args:
                    if '[' in arg and ']' in arg:
                        extract_temp = arg.split(',')
                        for num in extract_temp:
                            num = num.replace('[','')
                            num = num.replace(']','')
                            extract_numbers.append(int(num))
                    elif 'tags{' in arg or '{' in arg and '}' in arg:
                        extract_temp = arg.split(',')
                        for num in extract_temp:
                            num = num.replace('tags{','')
                            num = num.replace('}','')
                            tags.append(num)
            replied_message = await ctx.fetch_message(ctx.message.reference.message_id)
            for arg in replied_message.content.split(' '):
                if 't.co' in arg:
                    r = requests.get(arg)
                    tweet_url = r.url
                    break
                elif 'twitter.com' in arg:
                    tweet_url = arg
                    break
        elif 't.co' in args[0]:
            r = requests.get(args[0])
            tweet_url = r.url
        else:
            tweet_url = args[0]
        for item in tweet_url.split('/'):
            if trigger:
                tweet_id = item
                break
            else:
                if item == 'status':
                    trigger = True
        try:
            tweet = self.api.get_status(tweet_id, tweet_mode="extended")
        except:
            await ctx.send("invalid link probably")
        try:
            text = (tweet.retweeted_status.full_text)
        except AttributeError:  # Not a Retweet
            text = (tweet.full_text)
        if tags != []:
            text+='\nTags:'
            for tag in tags:
                text+='\n'+tag
        embed = discord.Embed(
            description = text,
            colour = embed_colour
        )
        embed.set_author(name=tweet.user.screen_name,icon_url=tweet.user.profile_image_url_https)
        embed.set_footer(text='Command requested by ' + str(ctx.message.author))
        if 'media' in tweet.entities:
            media = tweet.extended_entities['media']
            ##print(json.dumps(media,sort_keys=True, indent=4))
            file_stats = None
            counter_a = 1
            for item in media:
                if counter_a not in extract_numbers and extract_numbers 	!= []:
                    counter_a+=1
                    continue
                if 'video_info' in item:
                    for variant in item['video_info']['variants']:
                        if variant['content_type'] == 'video/mp4':
                            media_url = variant['url']
                            break
                    wget.download(media_url)
                    if item['type'] == 'animated_gif':
                        clip = VideoFileClip(media_url.split('/')[-1])
                        clip.write_gif('output.gif')
                        if (os.stat('output.gif').st_size/(1024*1024)) < 8:
                            await ctx.send(file=discord.File('output.gif'))
                            if sync:
                                await other_channels[ctx.channel.name].send(file=discord.File('output.gif', spoiler = spoiler_tag),embed=embed)
                        else:
                            await ctx.send(content="GIF file was too big.",file=discord.File(media_url.split('/')[-1].split('.mp4')[0]+'.mp4'))
                        await ctx.send(embed=embed)
                        os.remove('output.gif')
                        os.remove(media_url.split('/')[-1].split('.mp4')[0]+'.mp4')
                    else:
                        if (os.stat(media_url.split('/')[-1].split('.mp4')[0]+'.mp4')).st_size/(1024*1024) <= 8:
                            await ctx.send(file=discord.File(media_url.split('/')[-1].split('.mp4')[0]+'.mp4', spoiler = spoiler_tag),embed=embed)
                            if sync:
                                await other_channels[ctx.channel.name].send(file=discord.File(media_url.split('/')[-1].split('.mp4')[0]+'.mp4', spoiler = spoiler_tag),embed=embed)
                        else:
                            await ctx.send('Video was too large.')
                        os.remove(media_url.split('/')[-1].split('.mp4')[0]+'.mp4')
                elif item['type'] == 'photo':
                    media_url = item['media_url_https']
                    image = requests.get(media_url+':large')
                    if 200 == image.status_code:
                        with open(media_url.split('/')[-1], 'wb') as f:
                            f.write(image.content)
                    regular_file_name = media_url.split('/')[-1]
                    if resup:
                        res_file_name = media_url.split('/')[-1][:-4]+'_[L3][x2.00].png'
                        await self.bot.loop.run_in_executor(None, self.res_up_local, regular_file_name)
                        if (os.stat(res_file_name).st_size/(1024*1024)) > 8:
                            if item == media[-1]:
                                await ctx.send(file=discord.File(regular_file_name, spoiler = spoiler_tag),embed=embed)
                                if sync:
                                    await other_channels[ctx.channel.name].send(file=discord.File(regular_file_name, spoiler = spoiler_tag),embed=embed)
                            else:
                                await ctx.send(content="Res'd file was too big.",file=discord.File(regular_file_name, spoiler = spoiler_tag))
                            os.remove(regular_file_name)
                            os.remove(res_file_name)
                        else:
                            if item == media[len(extract_numbers)-1]:
                                await ctx.send(file=discord.File(res_file_name, spoiler = spoiler_tag),embed=embed)
                                if sync:
                                    await other_channels[ctx.channel.name].send(file=discord.File(res_file_name, spoiler = spoiler_tag),embed=embed)
                            else:
                                await ctx.send(file=discord.File(res_file_name, spoiler = spoiler_tag))
                                if sync:
                                    await other_channels[ctx.channel.name].send(file=discord.File(res_file_name, spoiler = spoiler_tag))
                            os.remove(res_file_name)
                            os.remove(regular_file_name)
                    else:
                        if item == media[len(extract_numbers)-1]:
                            await ctx.send(file=discord.File(regular_file_name, spoiler = spoiler_tag),embed=embed)
                            if sync:
                                await other_channels[ctx.channel.name].send(file=discord.File(regular_file_name, spoiler = spoiler_tag),embed=embed)
                        else:
                            await ctx.send(file=discord.File(regular_file_name, spoiler = spoiler_tag))
                            if sync:
                                await other_channels[ctx.channel.name].send(file=discord.File(regular_file_name, spoiler = spoiler_tag))
                        os.remove(regular_file_name)
                counter_a+=1
            await ctx.message.delete()



    # twitter slash
    @app_commands.command()
    async def twitter(
        self,
        interaction : discord.Interaction,
        url : str,
        resup : Optional[bool],
        spoiler_tag : Optional[bool],
        sync : Optional[bool],
        tags : Optional[str],
        extraction_numbers : Optional[str]
    ):
        await log(f'/twitter {url} by {interaction.user}')

        await interaction.response.defer()

        embed_colour = interaction.guild.self_role.colour

        if tags:
            tags = tags.split(",")

        if extraction_numbers:
            extraction_numbers = extraction_numbers.split(",")
        else:
            extraction_numbers = None

        if 't.co' in url:
            r = requests.get(url)
            tweet_url = r.url
        else:
            tweet_url = url

        # My current way of scanning for the tweet id, since I know status will come right before the id.
        Trigger = False
        for item in tweet_url.split('/'):
            if Trigger:
                tweet_id = item
                break
            else:
                if item == 'status':
                    Trigger = True

        try:
            tweet = self.api.get_status(tweet_id, tweet_mode="extended")
        except:
            await interaction.followup.send_message("Error 404, Most likely an invalid link.")

        try:
            text = (tweet.retweeted_status.full_text)
        except AttributeError:  # Not a Retweet
            text = (tweet.full_text)
        if tags: # prepare the tag text for the embeds
            text+='\nTags:'
            for tag in tags:
                text+='\n'+tag

        # embed making
        embed = discord.Embed( # make the embed
            description = text,
            colour = embed_colour
        )
        embed.set_author(name=tweet.user.screen_name,icon_url=tweet.user.profile_image_url_https)  # pull info on the tweeter
        embed.set_footer(text='Command requested by ' + str(interaction.user)) # set footer to requester of command

        # pulling the tweet
        if 'media' in tweet.entities: # check for media
            media = tweet.extended_entities['media']
            ##print(json.dumps(media,sort_keys=True, indent=4)) (debug line)
            file_stats = None
            counter_a = 1
            for item in media:
                if counter_a not in extraction_numbers and extraction_numbers:
                    counter_a+=1
                    continue
                if 'video_info' in item:
                    for variant in item['video_info']['variants']:
                        if variant['content_type'] == 'video/mp4':
                            media_url = variant['url']
                            break
                    wget.download(media_url)
                    if item['type'] == 'animated_gif':
                        clip = VideoFileClip(media_url.split('/')[-1])
                        clip.write_gif('output.gif')
                        if (os.stat('output.gif').st_size/(1024*1024)) < 8:
                            await interaction.followup.send(file=discord.File('output.gif'), embed=embed)
                            if sync:
                                await self.other_channels[interaction.channel.name].send(file=discord.File('output.gif', spoiler = spoiler_tag),embed=embed)
                        else:
                            await interaction.followup.send(content="GIF file was too big.",file=discord.File(media_url.split('/')[-1].split('.mp4')[0]+'.mp4'),embed=embed)
                        os.remove('output.gif')
                        os.remove(media_url.split('/')[-1].split('.mp4')[0]+'.mp4')
                    else:
                        if (os.stat(media_url.split('/')[-1].split('.mp4')[0]+'.mp4')).st_size/(1024*1024) <= 8:
                            await interaction.followup.send(file=discord.File(media_url.split('/')[-1].split('.mp4')[0]+'.mp4', spoiler = spoiler_tag),embed=embed)
                            if sync:
                                await self.other_channels[interaction.channel.name].send(file=discord.File(media_url.split('/')[-1].split('.mp4')[0]+'.mp4', spoiler = spoiler_tag),embed=embed)
                        else:
                            await interaction.followup.send('Video was too large.')
                        os.remove(media_url.split('/')[-1].split('.mp4')[0]+'.mp4')
                elif item['type'] == 'photo':
                    media_url = item['media_url_https']
                    image = requests.get(media_url+':large')
                    if 200 == image.status_code:
                        with open(media_url.split('/')[-1], 'wb') as f:
                            f.write(image.content)
                    regular_file_name = media_url.split('/')[-1]
                    if resup:
                        res_file_name = media_url.split('/')[-1][:-4]+'_[L3][x2.00].png'
                        await self.bot.loop.run_in_executor(None, self.res_up_local, regular_file_name)
                        if (os.stat(res_file_name).st_size/(1024*1024)) > 8:
                            if item == media[-1]:
                                await interaction.followup.send(file=discord.File(regular_file_name, spoiler = spoiler_tag),embed=embed)
                                if sync:
                                    await self.other_channels[interaction.channel.name].send(file=discord.File(regular_file_name, spoiler = spoiler_tag),embed=embed)
                            else:
                                await interaction.followup.send(content="Res'd file was too big.",file=discord.File(regular_file_name, spoiler = spoiler_tag))
                            os.remove(regular_file_name)
                            os.remove(res_file_name)
                        else:
                            if item == media[len(extraction_numbers)-1]:
                                await interaction.followup.send(file=discord.File(res_file_name, spoiler = spoiler_tag),embed=embed)
                                if sync:
                                    await self.other_channels[interaction.channel.name].send(file=discord.File(res_file_name, spoiler = spoiler_tag),embed=embed)
                            else:
                                await interaction.followup.send(file=discord.File(res_file_name, spoiler = spoiler_tag))
                                if sync:
                                    await self.other_channels[interaction.channel.name].send(file=discord.File(res_file_name, spoiler = spoiler_tag))
                            os.remove(res_file_name)
                            os.remove(regular_file_name)
                    else:
                        if item == media[len(extraction_numbers)-1]:
                            await interaction.followup.send(file=discord.File(regular_file_name, spoiler = spoiler_tag),embed=embed)
                            if sync:
                                await self.other_channels[interaction.channel.name].send(file=discord.File(regular_file_name, spoiler = spoiler_tag),embed=embed)
                        else:
                            await interaction.followup.send(file=discord.File(regular_file_name, spoiler = spoiler_tag))
                            if sync:
                                await self.other_channels[interaction.channel.name].send(file=discord.File(regular_file_name, spoiler = spoiler_tag))
                        os.remove(regular_file_name)
                counter_a+=1



    def res_up_local(self, filename): # goes with res_up
        scale, noise = 2, 3
        os.system("cmd /c w2x/waifu2x-converter-cpp -c 9 -q 101 --scale-ratio "+str(scale)+" --noise-level "+str(noise)+" -m noise-scale -i "+filename)



    def res_queue(self, item): # goes with res_up? i don't know if i still use this actually
        os.system("cmd /c waifu2x-converter-cpp -c 9 -q 101 --scale-ratio "+item[1][1]+" --noise-level "+item[1][0]+" -m noise-scale -i "+item[0])



    @app_commands.command()
    async def res_up(
        self,
        interaction : discord.Interaction,
        noise : Optional[Literal["1","2","3"]],
        scale : Optional[int],
        url : Optional[str],
        attachment : Optional[discord.Attachment] = None
    ):
        await interaction.response.defer()
        if not attachment and not url:
            await interaction.followup.send("You need an attachment or a URL for this to work.")
        elif attachment and url:
            await interaction.followup.send("Please only do one input at a time.")
        else:
            async with interaction.channel.typing():
                if not noise: # set defaults
                    noise = '3'
                if not scale:
                    scale = '2'
                if attachment: # if not url then url = attachment.url
                    url = attachment.url

                filename = os.path.basename(urlparse(url).path)
                item = [filename, (noise, scale)]
                response = requests.get(url, timeout=60)
                file = open(filename, "wb")
                file.write(response.content)
                file.close()
                if filename[-3:] == 'gif':
                    await interaction.followup.send("Please don't use gifs. Please.")
                else:
                    tasks = []
                    tasks.append(self.bot.loop.run_in_executor(None, self.res_queue, item))
                    await asyncio.wait(tasks)
                    res_file_name = item[0][:-4]+'_[L'+item[1][0]+'][x'+item[1][1]+'.00].png'
                    file_stats = os.stat(res_file_name)
                    if math.ceil(file_stats.st_size/(1024*1024)) > 8:
                        await interaction.followup.send('The result for this image was too large...')
                    else:
                        await interaction.followup.send('Command requested by '+str(interaction.user)+'.', file=discord.File(res_file_name))
                    os.remove(res_file_name)
                    os.remove(item[0])




