'''
Touhou Leaderboard
(With credit to the authors of THrep)

By 0x01FE#1244

'''

from threp import THReplay
from discord import app_commands
from discord.ext import commands
from typing import Optional
from typing import Literal

import discord
import requests
import os

LEADERBOARD_DATA_PATH = './data/leaderboard/'

class Leaderboard(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    '''
    Leaderboard file format (text) split by commas
    Rank Name TotalScore Character Difficulty SlowRate Date ReplayFileName
    0    1          2         3          4        6    7    8
    '''
    async def leaderboardAdd(self, interaction, game):
        replay = THReplay(LEADERBOARD_DATA_PATH + 'replays/temp.rpy')

        temp = replay.getBaseInfo().split(' ')

        character = temp[0] + ' ' + temp[1]
        difficulty = temp[2]
        rank = None
        leaderboardPath = LEADERBOARD_DATA_PATH + game + '.txt'

        stageScores = replay.getStageScore()
        totalScore = 0
        for score in stageScores:
            totalScore += score

        slowRate = replay.getSlowRate()
        player = replay.getPlayer()
        date = replay.getDate()
        filename = player + date.split(" ")[0] + character + '.rpy'
        Empty = False

        if os.path.exists(leaderboardPath):
            with open(LEADERBOARD_DATA_PATH + game + '.txt', 'r+') as f:
                lines = f.read()
                if lines == "":
                    Empty = True

            if Empty:
                rank = 1
                newScore = f'{rank}, {player}, {totalScore}, {character}, {difficulty}, {slowRate}, {date}, {filename}'
                lines = {newScore}
            else:
                with open(LEADERBOARD_DATA_PATH + game + '.txt', 'r+') as f:
                    lines = f.readlines()

                i = 0
                for line in lines:
                    lines[i] = line.split(",")
                    i+=1

                # Logic for looping through finding the place of newly added score
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

                    # kind of just trusting the user to upload a rpy
                    response = requests.get(url, timeout=60)
                    tempReplayPath = LEADERBOARD_DATA_PATH + "replays/temp.rpy"
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








