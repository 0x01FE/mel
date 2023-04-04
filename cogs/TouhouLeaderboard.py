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
        game : str
    ):
        replay = THReplay(f'{ REPLAYS_PATH }temp.rpy')

        temp = replay.getBaseInfo().split(' ')

        character = temp[0] + ' ' + temp[1]
        difficulty = temp[2]
        rank = None
        leaderboardPath = f'{ LEADERBOARD_PATH.format(interaction.guild_id) }{ game }.json'

        totalScore = 0
        for score in replay.getStageScore():
            totalScore += score

        slowRate = replay.getSlowRate()
        player = replay.getPlayer()
        date = replay.getDate()

        filename = player + date.split(" ")[0] + character + '.rpy'
        submittedRun = {"player" : player, "totalScore" : totalScore, "character" : character, "slowRate" : slowRate, "data" : date, "filename" : filename, "submitter" : str(interaction.user)}

        if os.path.exists(leaderboardPath):
            with open(leaderboardPath, 'r+') as f:
                leaderboard = json.loads(f.read())

            if not difficulty in leaderboard.keys():
                leaderboard[difficulty] = []
                leaderboard[0] = submittedRun

            else:
                # Logic for looping through data and finding the place of newly added score
                diffLeaderboard = leaderboard[difficulty]


                for i in range(0,len(diffLeaderboard)):

                    if diffLeaderboard[i]['totalScore'] > totalScore:

                        # If we're at the end of the array then slap the run there
                        if i-1 == len(diffLeaderboard):

                            # Insert new run
                            leaderboard[difficulty].insert(i, submittedRun)

                            # Done adding new run
                            break

                        # If we're not at the end of the array BUT we're larger than the next run and smaller than the last, we belong here.
                        elif diffLeaderboard[i+1]['totalScore'] < totalScore:

                            # Insert new run
                            leaderboard[difficulty].insert(i, submittedRun)









                i = 0
                for line in lines:
                    if (int(line[2]) > totalScore) and (int(lines[i+1][2]) < totalScore):
                        rank = int(line[0]) + 1

                        # Loop through ranks bellow yourself and increase them by 1
                        a = 0
                        startRankIncrease = False
                        for line2 in lines:
                            if line2 == line:
                                startRankIncrease = True
                            if startRankIncrease:
                                lines[a][0] = int(line2[0]) + 1
                            a+=1

                        newScore = f'{rank}, {player}, {totalScore}, {character}, {difficulty}, {slowRate}, {date}, {filename}'
                        lines.insert(i, newScore)
                    # change if you want to make pages for the leaderboard
                    if int(line[0]) > 10:
                        await interaction.response.send_message("You didn't make the top ten, L")
                        break
                    i+=1
        else:
            rank = 1
            newScore = f'{rank}, {player}, {totalScore}, {character}, {difficulty}, {slowRate}, {date}, {filename}'
            lines = {newScore}

        writeString = ''
        for line in lines:
            writeString += (line + '\n')

        with open(leaderboardPath, 'w+') as f:
            f.write(writeString)

        await interaction.response.send_message(f"Highscore added in rank {rank}")










    @app_commands.command()
    async def leaderboard(self,
        interaction : discord.Interaction,
        command : Literal['add','view', 'get'],
        game : Optional[str],
        replayname : Optional[str],
        attachment : Optional[discord.Attachment] = None
    ):
        if command == 'add':
            if attachment:
                if game:
                    url = attachment.url

                    # TODO : add check to see if the user did upload a replay file
                    response = requests.get(url, timeout=60)
                    tempReplayPath = LEADERBOARD_PATH + "replays/temp.rpy"
                    if not os.path.exists(tempReplayPath):
                        open(tempReplayPath, 'x')
                    file = open(tempReplayPath,'wb+')
                    file.write(response.content)
                    file.close()

                    await self.leaderboardAdd(interaction, game)
                else:
                    await interaction.response.send_message("Please select a game in the format of th#")

            else:
                await interaction.response.send_message("Please attach a replay file")
        elif command == 'view':
            if game:
                print('',end='')
            else:
                await interaction.response.send_message("Please select a game in the format of th#")
        elif command == 'get':
            if replayname:
                print('',end='')
            else:
                await interaction.response.send_message("Please select a replay file name.")
        else:
            await interaction.response.send_message(f"Error, command {command} was not recognised.")








