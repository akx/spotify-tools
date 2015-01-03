# -- encoding: UTF-8 --
import click
import logging

from spo.tools.playlist_gen import generate_playlist
from spo.tools.spotify_albums_to_tracks import spotify_albums_to_tracks
from spo.tools.spotify_search import spotify_search_albums, spotify_search_tracks
from spo.spotify import Spotify

known_tools = [
    generate_playlist,
    spotify_albums_to_tracks,
    spotify_search_albums,
    spotify_search_tracks
]


@click.group()
@click.option('-d', '--debug', 'log_level', flag_value=logging.DEBUG, help="Turn logging up to 11.")
@click.option('-v', '--verbose', 'log_level', flag_value=logging.INFO, help="Be informative.")
@click.option('--spotify-auth-token', 'spotify_auth_token', default=None, metavar="TOKEN", envvar="SPOTIFY_AUTH_TOKEN")
@click.option('--spotify-username', 'spotify_username', default=None, metavar="NAME", envvar="SPOTIFY_USERNAME")
def cli(log_level=logging.WARN, spotify_auth_token=None, spotify_username=None):
    if spotify_auth_token:
        Spotify.auth_token = spotify_auth_token

    if spotify_username:
        Spotify.auth_username = spotify_username

    logging.basicConfig(level=log_level)  # pragma: no cover

for tool in known_tools:
    cli.add_command(tool)
