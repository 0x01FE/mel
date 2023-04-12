'''
Touhou Leaderboard
(With credit to the authors of THrep)

By 0x01FE#1244

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


LEADERBOARD_DIR_PATH = '../data/leaderboard/{}/' # Will be formatted with guild id to keep leaderboards server specific
GLOBAL_LEADERBOARD_PATH = '../data/leaderboard/global/'
REPLAYS_DIR_PATH = '../data/leaderboard/replays/'
TEMP_REPLAY_PATH = '../data/temp/temp.rpy'

TOUHOU_GAME_ICON_PATH = '../data/assets/th-icon-links.json'


class Leaderboard(commands.GroupCog, name='leaderboard'):

    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        super().__init__()



    @app_commands.command(name='add')
    async def leaderboardAdd(self,
        interaction : discord.Interaction,
        game : str,
        attachment : discord.Attachment
    ):
        url = attachment.url

        # Format leaderboard path with guild id
        leaderboardPath = f'{ LEADERBOARD_DIR_PATH.format(interaction.guild_id) }{ game }.json'
        globalPath = f'{ GLOBAL_LEADERBOARD_PATH }{ game }.json'

        # TODO : add check to see if the user did upload a replay file
        response = requests.get(url, timeout=60)

        os.makedirs('../data/temp', exist_ok=True)

        with open(TEMP_REPLAY_PATH, 'wb+') as f:
            f.write(response.content)


        replays = glob(REPLAYS_DIR_PATH+"*")
        for replay in replays:
            if cmp(TEMP_REPLAY_PATH, replay):
                await interaction.response.send_message("That replay has already been uploaded.")
                return


        # Gathering info from the replay file
        replay = THReplay(TEMP_REPLAY_PATH)

        baseInfo = replay.getBaseInfo().split(' ')
        character = f'{ baseInfo[0] } { baseInfo[1] }'
        difficulty = baseInfo[2]

        stageScores = replay.getStageScore()
        endStage = len(stageScores)
        totalScore = stageScores[-1]


        slowRate = replay.getSlowRate()
        player = replay.getPlayer()
        date = replay.getDate()

        # Preparing the filename that the replay will be saved as in the records and the json entry for the leaderboard
        fileNumber = len(replays)+1

        filename = f'{ player }{ character.replace(" ", "-") }{ fileNumber }.rpy'

        submittedRun = {
            "player" : player,
            "totalScore" : totalScore,
            "character" : character,
            "slowRate" : slowRate,
            "data" : date,
            "filename" : filename,
            "submitter" : str(interaction.user),
            "endStage" : endStage
        }

        os.makedirs(LEADERBOARD_DIR_PATH.format(interaction.guild_id), exist_ok=True)
        os.makedirs(GLOBAL_LEADERBOARD_PATH, exist_ok=True)


        os.makedirs(REPLAYS_DIR_PATH, exist_ok=True)
        os.system(f"cp { TEMP_REPLAY_PATH } { REPLAYS_DIR_PATH }{ filename }")

        serverRank = await self.addScoreToJson(leaderboardPath, difficulty, submittedRun)
        globalRank = await self.addScoreToJson(globalPath, difficulty, submittedRun)

        await log(f"New highscore added by { interaction.user } in { interaction.guild.name }")
        await interaction.response.send_message(f"Highscore added in rank { serverRank } for { interaction.guild.name }\nGlobal Rank : { globalRank }", ephemeral=True)



    async def addScoreToJson(self, leaderboardPath, difficulty, submittedRun) -> int:

        if not os.path.exists(leaderboardPath):
            leaderboard = {}

            with open(leaderboardPath, 'w+') as f:
                f.write(json.dumps(leaderboard))

        else:
            with open(leaderboardPath, 'r') as f:
                leaderboard = json.loads(f.read())


        if difficulty not in leaderboard.keys():
            leaderboard[difficulty] = [submittedRun]
            rank = 1

        else:
            # Logic for looping through data and finding the place of newly added score
            diffLeaderboard = leaderboard[difficulty]

            for currentRunIndex in range(0, len(diffLeaderboard)):

                if diffLeaderboard[currentRunIndex]['totalScore'] > submittedRun['totalScore']:

                    # If we're at the end of the array then slap the run there
                    if currentRunIndex+1 == len(diffLeaderboard):
                        leaderboard[difficulty].append(submittedRun)
                        rank = currentRunIndex+1
                        break

                    # If we're not at the end of the array BUT we're larger than the next run and smaller than the last, we belong here.
                    elif diffLeaderboard[currentRunIndex+1]['totalScore'] < submittedRun['totalScore']:
                        leaderboard[difficulty].insert(currentRunIndex, submittedRun)
                        rank = currentRunIndex+1
                        break


                else:
                    leaderboard[difficulty].insert(currentRunIndex, submittedRun)
                    rank = currentRunIndex+1
                    break

        with open(leaderboardPath, 'w+') as f:
            f.write(json.dumps(leaderboard, indent=4))

        return rank



    @app_commands.command(name='view')
    async def leaderboardView(self,
        interaction : discord.Interaction,
        game : str,
        difficulty : Literal["Easy", "Normal", "Hard", "Lunatic"],
        globalview : Optional[bool],
        page : Optional[int]
    ):
        gameFull = await self.gameShortToGameFull(game)
        if globalview:

            with open(f'{ GLOBAL_LEADERBOARD_PATH }{ game }.json', 'r') as f:
                leaderboard = json.loads(f.read())

            embed = discord.Embed(title=f'Global { gameFull } Leaderboard')

        else:
            try:
                with open(f'{ LEADERBOARD_DIR_PATH.format(interaction.guild_id) }{ game }.json', 'r') as f:
                    leaderboard = json.loads(f.read())

            except FileNotFoundError:
                await interaction.response.send_message("Leaderboard not file, if think this was an error, I give you permission ping/dm 0x01FE#1244 until he responds.")

            embed = discord.Embed(title=f'{ interaction.guild.name } | { gameFull } Leaderboard')

        # Each page number just offsets by ten when reading the json
        if not page:
            page = 1


        embed.color = randint(0, 0xFFFFFF)
        embed.description = f'Difficulty : { difficulty }'

        leaderboardContent = ''

        if len(leaderboard[difficulty]) < 10:
            end = len(leaderboard[difficulty])
            start = 0

        else:
            end = 10+((page-1)*10)
            start = ((page-1)*10)

        for run in range(start, end):

            runInfo = leaderboard[difficulty][run]

            entry = '{}. {}, {}, Score: {}, Slow Rate: {}, End Stage: {}'.format(
                run+1,
                runInfo['player'],
                runInfo['character'],
                runInfo['totalScore'],
                runInfo['slowRate'],
                runInfo['endStage']
            )


            leaderboardContent = leaderboardContent + entry + '\n'

        embed.add_field(name=f'Leaderboard Page { page }', value=leaderboardContent)

        with open(TOUHOU_GAME_ICON_PATH, 'r') as f:
            iconLink = json.loads(f.read())[game]

        embed.set_thumbnail(url=iconLink)

        await interaction.response.send_message(embed=embed)



    # Yes I know i could use a match case but i have the bot on a python 3.10 image and i'm lazy
    async def gameShortToGameFull(self, gameShort):
        if gameShort == 'th1':
            return "Touhou 1 : Highly Responsive to Prayers"
        elif gameShort == 'th2':
            return "Touhou 2 : Story of Eastern Wonderland"
        elif gameShort == 'th3':
            return "Touhou 3 : Phantasmagoria of Dim.Dream"
        elif gameShort == 'th4':
            return "Touhou 4 : Lotus Land Story"
        elif gameShort == 'th5':
            return "Touhou 5 : Mystic Square"
        elif gameShort == 'th6':
            return "Touhou 6 : Embodiment of Scarlet Devil"
        elif gameShort == 'th7':
            return "Touhou 7 : Perfect Cherry Blossom"
        elif gameShort == 'th8':
            return "Touhou 8 : Imperishable Night"
        elif gameShort == 'th10':
            return "Touhou 10 : Mountain of Faith"
        elif gameShort == 'th11':
            return "Touhou 11 : Subterranean Animism"
        elif gameShort == 'th12':
            return "Touhou 12 : Undefined Fantastic Object"
        elif gameShort == 'th13':
            return "Touhou 13 : Ten Desires"
        elif gameShort == 'th14':
            return "Touhou 14 : Double Dealing Character"
        elif gameShort == 'th15':
            return "Touhou 15 : Legacy of Lunatic Kingdom"
        elif gameShort == 'th16':
            return "Touhou 16 : Hidden Star in Four Seasons"
        elif gameShort == 'th17':
            return "Touhou 17 : Wily Beast and Weakest Creature"
        elif gameShort == 'th18':
            return "Touhou 18 : Unconnected Marketeers"






