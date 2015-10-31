# -- encoding: UTF-8 --
import json
import logging
import sys

import click
from spo.spotify import Spotify
from spo.file_processor import FileProcessor


log = logging.getLogger(__name__)


class SpotifyAlbumURLsToTrackURLs(FileProcessor):
    def fp_init(self, **kwargs):
        self.spotify = Spotify()

    def process_uri(self, uri):
        try:
            datum = self.spotify.album(uri)
        except:
            self._write(u"# failed: %s" % uri)
            self._write(u"# error: %s" % repr(sys.exc_info()))
            return
        self._write("# + %s" % json.dumps({
            "uri": uri,
            "artists": [a["name"] for a in datum["artists"]],
            "name": datum["name"],
        }))
        for num, track in enumerate(datum["tracks"]["items"], 1):
            self._write(u"#- %d - %s" % (num, track["name"]))
            self._write(track["href"])
        self._write()

    def run(self):
        for line in self.input:
            line = line.strip()
            if line.startswith(u"spotify:album:"):
                self.process_uri(line)


@click.command("spotify-albums-to-tracks", short_help="Convert a list of Spotify album URIs into a list of Spotify track URIs.")
@click.argument("input", type=click.File("rb"), required=True)
@click.option("--output", "-o", type=click.File("wb"), default=sys.stdout)
def spotify_albums_to_tracks(input, output):  # pragma: no cover
    SpotifyAlbumURLsToTrackURLs(input=input, output=output).run()
