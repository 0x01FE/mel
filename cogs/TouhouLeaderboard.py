'''
Touhou Leaderboard
(With credit to the authors of THrep)

By 0x01FE#1244

'''
import discord
from discord import app_commands
from discord.ext import commands

from typing import Optional
from typing import Literal

import requests
import os
import json
from threp import THReplay


LEADERBOARD_PATH = '../data/leaderboard/{}/' # Will be formatted with guild id to keep leaderboards server specific
REPLAYS_PATH = '../data/leaderboard/'


class Leaderboard(commands.GroupCog, name='leaderboard'):

    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    '''
    Leaderboard file format (json)
    Name TotalScore Character SlowRate Date ReplayFileName Submitter
    1          2         3    4        5    6              7
    Rank = index of run + 1
    '''

    @app_commands.command(name='add')
    async def leaderboardAdd(self,
        interaction : discord.Interaction,
        game : str,
        attachment : discord.Attachment
    ):
        url = attachment.url

        # Format leaderboard path with guild id
        leaderboardPath = f'{ LEADERBOARD_PATH.format(interaction.guild_id) }{ game }.json'

        # TODO : add check to see if the user did upload a replay file
        response = requests.get(url, timeout=60)
        tempReplayPath = f'{ LEADERBOARD_PATH.format(interaction.guild_id) }replays/temp.rpy'

        if not os.path.exists(tempReplayPath):
            open(tempReplayPath, 'x')

        with open(tempReplayPath, 'wb+') as f:
            f.write(response.content)

        # Gathering info from the replay file
        replay = THReplay(f'{ REPLAYS_PATH }temp.rpy')

        with replay.getBaseInfo().split(' ') as baseInfo:
            character = f'{ baseInfo[0] } { baseInfo[1] }'
            difficulty = baseInfo[2]

        rank = None

        totalScore = 0
        for score in replay.getStageScore():
            totalScore += score

        slowRate = replay.getSlowRate()
        player = replay.getPlayer()
        date = replay.getDate()

        # Preparing the filename that the replay will be saved as in the records and the json entry for the leaderboard
        filename = player + date.split(" ")[0] + character + '.rpy'
        submittedRun = {"player" : player, "totalScore" : totalScore, "character" : character, "slowRate" : slowRate, "data" : date, "filename" : filename, "submitter" : str(interaction.user)}

        os.makedirs(leaderboardPath, exist_ok=True)


        with open(leaderboardPath, 'r+') as f:
            leaderboard = json.loads(f.read())

        if difficulty not in leaderboard.keys():
            leaderboard[difficulty] = []
            leaderboard[0] = submittedRun

        else:
            # Logic for looping through data and finding the place of newly added score
            diffLeaderboard = leaderboard[difficulty]

            for currentRunIndex in range(0, len(diffLeaderboard)):

                if diffLeaderboard[currentRunIndex]['totalScore'] > totalScore:

                    # If we're at the end of the array then slap the run there
                    if currentRunIndex-1 == len(diffLeaderboard):
                        leaderboard[difficulty].insert(currentRunIndex, submittedRun)
                        break

                    # If we're not at the end of the array BUT we're larger than the next run and smaller than the last, we belong here.
                    elif diffLeaderboard[currentRunIndex+1]['totalScore'] < totalScore:
                        leaderboard[difficulty].insert(currentRunIndex, submittedRun)

                else:
                    leaderboard[difficulty].insert(currentRunIndex, submittedRun)


        with open(leaderboardPath, 'w+') as f:
            f.write(json.dumps(leaderboard))

        await interaction.response.send_message(f"Highscore added in rank {rank}")










