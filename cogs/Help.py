import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from typing import Literal

BOT_AUTHOR = '0x01FE#1244'
BOT_PFP = 'ar15face.png'



class MyHelpCommand(commands.MinimalHelpCommand):
    pass

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = MyHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


'''
class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None


    @app_commands.command() # TODO make into better for each seperate command
    async def help(
        self,
        interaction : discord.Interaction,
        cmd : Optional[ Literal[
            'ping',
            'twitter',
            'res_up',
            'dicer',
            'channel_scroll',
            'tag',
            'set',
            'leave',
            'ar15face',
            'k11',
            'sodumb'
            ] ]
    ):
        # universal embed setup
        embed_colour = interaction.guild.self_role.colour # this isn't grabbing role color
        thumbnail = discord.File("data/assets/" + BOT_PFP, filename = BOT_PFP)
        embed_init = discord.Embed(
            title = "Help Menu",
            description = 'Welcome to the help menu.',
            colour = embed_colour
        )
        embed_init.set_footer(text = 'Bot developed by ' + BOT_AUTHOR + ".")
        embed_init.set_thumbnail(url = "attachment://" + BOT_PFP)

        if cmd is None:
            embed = await self.helpmenu(embed_init)
        elif cmd == 'ping':
            embed = await self.ping(embed_init)



            await interaction.response.send_message(file=thumbnail,embed=embed)




    async def helpmenu(self, embed: discord.Embed):
        embed.add_field(name='/help', value='> Brings up this help menu.',inline=False)
        embed.add_field(name='/ping', value='> Ask the bot if it is still alive.',inline=False)
        embed.add_field(name='/twitter', value='> Rip video(s), gif(s), or image(s) from a twitter post.\n > **Usage:** `-twitter (link) (res_up [optinal]) (sp or spoiler) ([*] where * = the numbers for the images you want extracted) (tags{tag1,tag2} make sure you have no spaces) (sync)`\n **Example:** -twitter (link) res_up (would do the thing and res the image up as well)',inline=False)
        embed.add_field(name='/res_up', value='> Reply to or post an image with this command and up the resolution!\n > **Usage:** `-res_up (noise amount [1-3]) (resolution multiplier [2 is reccomended]) (image [or reply to an image])`',inline=False)
        embed.add_field(name='/dicer', value='> Want to make an image into dice?\n > **Usage:** `-dicer (image)`',inline=False)
        embed.add_field(name='/channel_scroll', value='> Use an embed to scroll through images in the current channel. (give the bot some time to get all the images)',inline=False)
        embed.add_field(name='/tag',value='> has 4 options, GET (name) gets a tag by name, CREATE (name) (attachment) takes an image or gif and makes a tag for it, DELETE (name) deletes the tag with given name, LIST lists all tags',inline=False)
        embed.add_field(name='/set', value = '> settings for the bot. (brings up seperate help menu)', inline=False)
        embed.add_field(name='/leave', value='> Have the bot leave the call.',inline=False)
        embed.add_field(name='/ar15face', value='> Post the funny face.',inline=False)
        embed.add_field(name='/k11', value='> Say the funny thing.',inline=False)
        embed.add_field(name='/sodumb', value='> Send the funny gif.',inline=False)
        return embed





'''



