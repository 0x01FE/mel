'''
Touhou Leaderboard
(With credit to the authors of THrep)

By 0x01FE

'''
import discord
from discord import app_commands
from discord.ext import commands

from threp import THReplay

from typing import Optional
from typing import Literal

import requests
import os
import json
from glob import glob
from filecmp import cmp
from datetime import datetime
from random import randint

from .Utils import log
from .Leaderboard import Leaderboard

GLOBAL_LEADERBOARD_PATH = '../data/leaderboard/global/'
LEADERBOARD_DIR_PATH = '../data/leaderboard/{}/' # Will be formatted with guild id to keep leaderboards server specific
REPLAYS_DIR_PATH = '../data/leaderboard/{}/replays/'
TEMP_REPLAY_PATH = '../data/temp/temp.rpy'

TOUHOU_GAME_ICON_PATH = '../data/assets/th-icon-links.json'

class LeaderboardCog(commands.GroupCog, name='leaderboard'):

    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        super().__init__()

        if not os.path.exists('../data/temp'):
            os.makedirs('../data/temp')

        if not os.path.exists('../data/leaderboard'):
            os.makedirs('../data/leaderboards')


    @app_commands.command(name='add')
    @app_commands.guild_only()
    async def leaderboardAdd(self,
        interaction : discord.Interaction,
        game : str,
        attachment : discord.Attachment
    ):
        if not interaction.guild_id or not interaction.guild:
            await interaction.response.send_message("This command only works in servers. If you believe this is an error please send a message to 0x01fe on Discord.")
            return

        add_to_global = True
        url = attachment.url

        # TODO : add check to see if the user did upload a replay file
        response = requests.get(url, timeout=60)

        server_leaderboard = Leaderboard(interaction.guild_id)
        global_leaderboard = Leaderboard("global")

        with open(TEMP_REPLAY_PATH, 'wb+') as f:
            f.write(response.content)

        # Check if replay has been uploaded to this server

        server_replays = glob(server_leaderboard.replays_dir)
        for replay in server_replays:
            if cmp(TEMP_REPLAY_PATH, replay):
                await interaction.response.send_message("That replay has already been uploaded to this server.")
                return

        # Check if this replay is on the global leaderboard
        global_replays = glob(GLOBAL_LEADERBOARD_PATH + "*")
        for replay in global_replays:
            if cmp(TEMP_REPLAY_PATH, replay):
                await log("Replay already on global leaderboard")
                add_to_global = False

        # Create filename
        replay = THReplay(TEMP_REPLAY_PATH)
        baseInfo = replay.getBaseInfo().split(' ')
        character = f'{ baseInfo[0] } { baseInfo[1] }'
        file_number = len(server_replays) + 1


        file_name = f'{ replay.getPlayer() }{ character.replace(" ", "-") }{ file_number }.rpy'

        os.system(f"cp { TEMP_REPLAY_PATH } { server_leaderboard.replays_dir }{ file_name }")
        server_rank = await server_leaderboard.add(file_name, str(interaction.user), game)

        await interaction.response.send_message()

        if add_to_global:
            os.system(f"cp { TEMP_REPLAY_PATH } { global_leaderboard.replays_dir }{ file_name }")
            global_rank = await global_leaderboard.add(file_name, str(interaction.user), game)


        await log(f"New highscore added by { interaction.user } in { interaction.guild.name }")
        await interaction.response.send_message(f"Highscore added in rank { server_rank } for { interaction.guild.name }", ephemeral=True)

        if add_to_global:
            await interaction.response.send_message(f"Global Rank : { global_rank }", ephemeral=True)




    '''
    You should maybe internalise most of this view into the leaderboard class
    have the leaderboard class have a method that outputs a nice view or something as a string
    '''
    @app_commands.command(name='view')
    @app_commands.guild_only()
    async def leaderboardView(self,
        interaction : discord.Interaction,
        game : str,
        difficulty : Literal["Easy", "Normal", "Hard", "Lunatic"],
        globalview : Optional[bool],
        page : Optional[int]
    ):
        if not interaction.guild_id or not interaction.guild:
            await interaction.response.send_message("This command only works in servers. If you believe this is an error please send a message to 0x01fe on Discord.")
            return

        gameFull = await self.gameShortToGameFull(game)

        if globalview:
            server = Leaderboard("global")
            embed = discord.Embed(title=f'Global { gameFull } Leaderboard')

        else:
            server = Leaderboard(interaction.guild_id)
            embed = discord.Embed(title=f'{ interaction.guild.name } | { gameFull } Leaderboard')

        # Each page number just offsets by ten when reading the json
        if not page:
            page = 1

        embed.color = randint(0, 0xFFFFFF)
        embed.description = f'Difficulty : { difficulty }'

        if len(server.leaderboard[difficulty]) < 10:
            end = len(server.leaderboard[difficulty])
            start = 0

        else:
            end = 10+((page-1)*10)
            start = ((page-1)*10)

        leaderboard_content = server.view(range(start, end), game, difficulty)

        embed.add_field(name=f'Leaderboard Page { page }', value=leaderboard_content)

        with open(TOUHOU_GAME_ICON_PATH, 'r') as f:
            iconLink = json.loads(f.read())[game]

        embed.set_thumbnail(url=iconLink)

        await interaction.response.send_message(embed=embed)



    # Yes I know i could use a match case but i have the bot on a python 3.10 image and i'm lazy
    # what are you on about you have it on 3.8 brother
    async def gameShortToGameFull(self, game_short : str):
        if game_short == 'th1':
            return "Touhou 1 : Highly Responsive to Prayers"
        elif game_short == 'th2':
            return "Touhou 2 : Story of Eastern Wonderland"
        elif game_short == 'th3':
            return "Touhou 3 : Phantasmagoria of Dim.Dream"
        elif game_short == 'th4':
            return "Touhou 4 : Lotus Land Story"
        elif game_short == 'th5':
            return "Touhou 5 : Mystic Square"
        elif game_short == 'th6':
            return "Touhou 6 : Embodiment of Scarlet Devil"
        elif game_short == 'th7':
            return "Touhou 7 : Perfect Cherry Blossom"
        elif game_short == 'th8':
            return "Touhou 8 : Imperishable Night"
        elif game_short == 'th10':
            return "Touhou 10 : Mountain of Faith"
        elif game_short == 'th11':
            return "Touhou 11 : Subterranean Animism"
        elif game_short == 'th12':
            return "Touhou 12 : Undefined Fantastic Object"
        elif game_short == 'th13':
            return "Touhou 13 : Ten Desires"
        elif game_short == 'th14':
            return "Touhou 14 : Double Dealing Character"
        elif game_short == 'th15':
            return "Touhou 15 : Legacy of Lunatic Kingdom"
        elif game_short == 'th16':
            return "Touhou 16 : Hidden Star in Four Seasons"
        elif game_short == 'th17':
            return "Touhou 17 : Wily Beast and Weakest Creature"
        elif game_short == 'th18':
            return "Touhou 18 : Unconnected Marketeers"






