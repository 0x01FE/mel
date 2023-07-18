from .Utils import log
from threp import THReplay

from typing import Union

import os
import json
from glob import glob


LEADERBOARD_DIR_PATH = '../data/leaderboard/{}/' # Will be formatted with guild id to keep leaderboards server specific
REPLAYS_DIR_PATH = '../data/leaderboard/{}/replays/'
TEMP_REPLAY_PATH = '../data/temp/temp.rpy'

class Leaderboard():

    # Server id should be the discord server id OR global
    def __init__(self, server_id : Union[int, str]) -> None:

        self.server_id = server_id
        self.dir = LEADERBOARD_DIR_PATH.format(server_id)
        self.replays_dir = REPLAYS_DIR_PATH.format(server_id)
        self.leaderboard = {} # Dict of lists of Run objects keyed by difficulty keyed by game

        # Create leaderboard if it doesn't exist
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

            # Create file for each of the games
            for game in range(1, 18 + 1):
                temp_leaderboard = {}

                # Add each difficulty to the json
                for difficulty in ["Easy", "Normal", "Hard", "Lunatic"]:
                    temp_leaderboard[difficulty] = []

                with open(f"{ self.dir }th{game}", "w") as f:
                    f.write(json.dumps(temp_leaderboard, indent=4))

        # If it does exist, load it
        else:
            # Loop through each file looking if it's empty or not, if it's not empty add it to the object
            leaderboards = glob(self.dir + "*")

            for leaderboard in leaderboards:
                with open(leaderboard, "r") as f:
                    leaderboard_data = json.loads(f.read())

                if leaderboard_data:
                    game = leaderboard.split("/")[-1].split(".")[0]

                    self.leaderboard[game] = leaderboard_data



    '''
    Returns server rank and global rank

    Repeat checking will be done outside of the class (in the bot).
    '''
    async def add(self, replay_name : str, user : str, game : str) -> int:

        replay = THReplay(f"{ self.replays_dir }{ replay_name }")
        rank = 1

        submitted_run = Run(replay, user, replay_name)

        if game not in self.leaderboard:
            self.leaderboard[game] = {}

        if submitted_run.difficulty not in self.leaderboard:
            self.leaderboard[game][submitted_run.difficulty] = [ submitted_run.json() ]
            await self.save()
            return rank

        # Logic for placing a run on the leaderboard
        else:
            temp_leaderboard = self.leaderboard[game][submitted_run.difficulty]

            run_count = len(temp_leaderboard)

            for run_index in range(0, run_count):

                if temp_leaderboard[run_index]['totalScore'] > submitted_run.total_score:

                    # If we're at the end of the array then slap the run there
                    if (run_index + 1) == run_count:
                        temp_leaderboard.append(submitted_run)
                        rank = run_index + 1
                        break

                    # If we're not at the end of the array BUT we're larger than the next run and smaller than the last, we belong here.
                    # I'm like 90% sure i don't even need this check
                    elif temp_leaderboard[run_index + 1]['totalScore'] < submitted_run.total_score:
                        temp_leaderboard.insert(run_index + 1, submitted_run)
                        rank = run_index + 2
                        break

                else:
                    temp_leaderboard.insert(run_index, submitted_run)
                    rank = run_index + 1
                    break

            self.leaderboard[game][submitted_run.difficulty] = temp_leaderboard
            await self.save()
            return rank



    # Mostly meant as an internal method to save the contents of the object to json files
    async def save(self) -> None:

        await log(f"Saving leaderboard data for server {self.server_id}...")

        for game in self.leaderboard:
            temp_game_leaderboard = {} # Temporary dict for converting all run objects to json

            for difficulty in self.leaderboard[game]:
                temp_game_leaderboard[difficulty] = []

                for run in self.leaderboard[game][difficulty]:
                    temp_game_leaderboard[difficulty].append(run.json())

            with open(f"{ self.dir }{ game }.json", "w+") as f:
                f.write(json.dumps(self.leaderboard[game], indent=4))



    '''
    Outputs a nicely formatted string to view the leaderboard for a games difficulty
    '''
    async def view(self, view_range : range, game : str, difficuly : str) -> str:
        temp_view =''

        requested_leaderboard = self.leaderboard[game][difficuly]

        for run_index in view_range:
            run = requested_leaderboard[run_index]

            temp_view += f'{ run_index }. { run.player }, { run.character }, Score: { run.total_score }, Slow Rate: { run.slow_rate }, End Stage: { run.end_stage }\n'

        return temp_view




class Run():

    def __init__(self, replay : THReplay, user : str, filename : str) -> None:

        self.base_info = replay.getBaseInfo().split(' ')
        self.character = f'{ self.base_info[0] } { self.base_info[1] }'
        self.difficulty = self.base_info[2]

        self.stage_scores = replay.getStageScore()
        self.end_stage = len(self.stage_scores)
        self.total_score = self.stage_scores[-1]

        self.slow_rate = replay.getSlowRate()
        self.player = replay.getPlayer()
        self.date = replay.getDate()
        self.user = user
        self.filename = filename


    def json(self) -> dict:
        return {
            "player" : self.player,
            "totalScore" : self.total_score,
            "character" : self.character,
            "slowRate" : self.slow_rate,
            "data" : self.date,
            "filename" : self.filename,
            "submitter" : self.user,
            "endStage" : self.end_stage
        }

