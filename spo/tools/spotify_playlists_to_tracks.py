# -- encoding: UTF-8 --
from itertools import count
import json
import logging
import sys

import click
import re
from spo.spotify import Spotify, SpotifyException
from spo.file_processor import FileProcessor


log = logging.getLogger(__name__)

PLAYLIST_URI_RE = re.compile("^spotify:user:(.+?):playlist:(.+?)$")


class SpotifyPlaylistsToTracks(FileProcessor):
    def fp_init(self, **kwargs):
        self.spotify = Spotify(auth=True)

    def get_playlist_tracks(self, username, playlist_id):
        step = 100
        tracks = []
        for offset in count(0, step=step):
            info = self.spotify.user_playlist_tracks(username, playlist_id, limit=step, offset=offset)
            tracks.extend(info["items"])
            if not info.get("next"):
                break
        return tracks

    def process_uri(self, uri):
        username, playlist_id = PLAYLIST_URI_RE.match(uri).groups()
        try:
            playlist = self.spotify.user_playlist(username, playlist_id)
        except SpotifyException, sexc:
            if sexc.http_status == 404:
                log.warn("Not found: %s" % uri)
                self._write("# - %s" % uri)
                return
            raise
        self._write("# + %s" % uri)
        self._write("# : %s" % json.dumps({"name": playlist["name"], "description": playlist["description"]}))

        pl_tracks = self.get_playlist_tracks(username, playlist_id)
        for i, pl_track in enumerate(pl_tracks):
            track = pl_track["track"]
            self._write("# %s" % json.dumps({
                "artists": [a["name"] for a in track.get("artists", ())],
                "name": track["name"],
                "added_at": pl_track.get("added_at"),
            }, sort_keys=True))
            self._write("%s" % track["uri"])

    def run(self):
        for line in self.input:
            line = line.strip()
            if line.startswith("spotify:user:") and ":playlist:" in line:
                self.process_uri(line)


@click.command("spotify-playlists-to-tracks", short_help="Convert a list of Spotify playlist URIs into a list of Spotify track URIs.")
@click.argument("input", type=click.File("rb"), required=True)
@click.option("--output", "-o", type=click.File("wb"), default=sys.stdout)
def spotify_playlists_to_tracks(input, output):  # pragma: no cover
    SpotifyPlaylistsToTracks(input=input, output=output).run()
