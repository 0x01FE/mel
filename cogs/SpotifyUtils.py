import discord
#import spotipy
import aiohttp
#import aiofiles
from urllib.parse import urlparse
from discord import app_commands
from discord.ext import commands
#from spotipy.oauth2 import SpotifyOAuth
import json
from typing import Optional

class SpotifyUtils(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        '''
        # can't log into spotify api properly on a server i think
        if bot.config['bot']['server']:
            scope = 'playlist-read-private user-modify-playback-state user-read-playback-state user-read-currently-playing user-library-read'
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
        '''


        with open("artistGenreMap.json", "r+") as f:
            self.artistGenreMap = json.loads(f.read())
    

    async def get_uri(self, url):
        return self.sp.track(url)['uri']


    @app_commands.command()
    async def genre(self, interaction : discord.Interaction,
        artist_name : str
    ):
        response = f"{artist_name}'s genres are "

        for genre in self.artistGenreMap[artist_name.lower()]:
            if genre == self.artistGenreMap[artist_name.lower()][-1]:
                response+="and "+genre
            else:
                response+=genre+", "
        
        await interaction.response.send_message(response)


    @app_commands.command()
    async def artistalbumsinfo(self, interaction : discord.Interaction,
        artist_url : str,
        year : Optional[str]
    ):
        artist_uri = await self.get_uri(artist_url)
        albums = self.sp.artist_albums(artist_uri)
        
        
        filtered_albums = []
        for album in albums['items']:
            release_year = album['release-date'].split("-")[0]
            name = album['name']
            image_url = album['images'][0]['url']

            if year is not None:
                if release_year == year:
                    filtered_albums.append((name, image_url, release_year))
            else:
                filtered_albums.append((name, image_url, release_year))

        for name, url, release_year in filtered_albums:

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        f = await aiofiles.open('./cmds/album_images/cover.png', mode='wb+')
                        await f.write(await resp.read())
                        await f.close()
            
                await interaction.response.send_message(f"__**{name} - {release_year}**__",file=discord.File('./cmds/album_images/cover.png'))



    
