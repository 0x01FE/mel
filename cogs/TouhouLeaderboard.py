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
from datetime import datetime

from .Utils import log


LEADERBOARD_DIR_PATH = '../data/leaderboard/{}/' # Will be formatted with guild id to keep leaderboards server specific
REPLAYS_DIR_PATH = '../data/leaderboard/replays'
TEMP_REPLAY_PATH = '../data/temp/temp.rpy'


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

        # TODO : add check to see if the user did upload a replay file
        response = requests.get(url, timeout=60)

        os.makedirs('../data/temp', exist_ok=True)

        with open(TEMP_REPLAY_PATH, 'wb+') as f:
            f.write(response.content)

        # Gathering info from the replay file
        replay = THReplay(TEMP_REPLAY_PATH)

        baseInfo = replay.getBaseInfo().split(' ')
        character = f'{ baseInfo[0] } { baseInfo[1] }'
        difficulty = baseInfo[2]

        totalScore = 0
        stageScores = replay.getStageScore()
        endStage = len(stageScores)

        for score in stageScores:
            totalScore += score

        slowRate = replay.getSlowRate()
        player = replay.getPlayer()
        date = replay.getDate()

        # Preparing the filename that the replay will be saved as in the records and the json entry for the leaderboard
        unixTimestamp = (datetime.now() - datetime(1970, 1, 1)).total_seconds()

        filename = f'{ player }{ character }{ unixTimestamp }.rpy'

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

                if diffLeaderboard[currentRunIndex]['totalScore'] > totalScore:

                    # If we're at the end of the array then slap the run there
                    if currentRunIndex+1 == len(diffLeaderboard):
                        leaderboard[difficulty].append(submittedRun)
                        rank = currentRunIndex+1
                        break

                    # If we're not at the end of the array BUT we're larger than the next run and smaller than the last, we belong here.
                    elif diffLeaderboard[currentRunIndex+1]['totalScore'] < totalScore:
                        leaderboard[difficulty].insert(currentRunIndex, submittedRun)
                        rank = currentRunIndex+1
                        break


                else:
                    leaderboard[difficulty].insert(currentRunIndex, submittedRun)
                    rank = currentRunIndex+1
                    break

        os.makedirs(REPLAYS_DIR_PATH, exist_ok=True)
        os.system(f"cp { TEMP_REPLAY_PATH } { REPLAYS_DIR_PATH }{ filename }")

        with open(leaderboardPath, 'w+') as f:
            f.write(json.dumps(leaderboard, indent=4))

        await log(f"New highscore added by { interaction.user } in { interaction.guild.name } in rank { rank }")
        await interaction.response.send_message(f"Highscore added in rank { rank }")










