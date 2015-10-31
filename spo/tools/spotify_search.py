import json
import logging
import sys

import click
from spo.spotify import Spotify
from spo.file_processor import FileProcessor

log = logging.getLogger(__name__)


class ListToSpotifyURLs(FileProcessor):

    def __init__(self, mode, input, output, encoding="UTF-8"):
        self.mode = mode
        if self.mode not in ("track", "album"):  # pragma: no cover
            raise NotImplementedError("Ni: %s" % self.mode)

        self.spotify = Spotify()
        super(ListToSpotifyURLs, self).__init__(input, output, encoding)

    def run(self):
        for line in self._read_lines():
            self._process_line(line)

    def _process_line(self, line):
        if line.startswith("Various - "):
            q = line.replace("Various - ", "")
        else:
            q = line.replace(" - ", " ")
        data = self.spotify.search(q=q, limit=5, type=self.mode)
        try:
            search_result = data["%ss" % self.mode]["items"][0]
        except (KeyError, IndexError):
            log.info("No result for %r", q)
            self._write(u"# - %s" % json.dumps({"q": q}))
            self._write()
            return

        log.info("Found result for %r", q)
        uri = search_result["uri"]
        if self.mode == "album":
            datum = self.spotify.album(uri)
        else:
            datum = self.spotify.track(uri)

        self._write(u"# + %s" % json.dumps({
            "q": q,
            "artists": [a["name"] for a in datum["artists"]],
            "name": datum["name"],
        }))
        self._write(u"%s" % uri)
        self._write()


@click.command("spotify-search-albums", short_help="search for albums in Spotify")
@click.argument("input", type=click.File("rb"), required=True)
@click.option("--output", "-o", type=click.File("wb"), default=sys.stdout)
def spotify_search_albums(input, output):  # pragma: no cover
    ListToSpotifyURLs(mode="album", input=input, output=output).run()


@click.command("spotify-search-tracks", short_help="search for tracks in Spotify")
@click.argument("input", type=click.File("rb"), required=True)
@click.option("--output", "-o", type=click.File("wb"), default=sys.stdout)
def spotify_search_tracks(input, output):  # pragma: no cover
    ListToSpotifyURLs(mode="track", input=input, output=output).run()
