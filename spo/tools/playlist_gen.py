# -- encoding: UTF-8 --
from contextlib import contextmanager

import hashlib
import logging
from StringIO import StringIO

from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader

import click
import codecs
import os
from spo.lastfm import LastFMAPI
from spo.spotify import Spotify
from spo.file_processor import FileProcessor
from spo.util import flatten
from spo.youtube import YoutubeAPI
from spo.yt_matcher import YoutubeMatcher


log = logging.getLogger(__name__)

class BaseTrack(dict):
    def get_artist_string(self):
        return ", ".join(a["name"] for a in self.get("artists", ()))

    artist = property(get_artist_string)


class PseudoTrack(BaseTrack):
    def __init__(self, string, separator=" - "):
        super(PseudoTrack, self).__init__()
        artist, title = unicode(string).split(separator, 1)
        self["artists"] = [{"name": artist}]
        self["name"] = title
        self["href"] = "pseudo:%s" % hashlib.md5(string.encode("UTF-8")).hexdigest()


class SpotifyTrack(BaseTrack):
    def __init__(self, iterable=None, **kwargs):
        super(SpotifyTrack, self).__init__(iterable, **kwargs)
        uri = self["uri"]
        self["open_spotify_url"] = "http://open.spotify.com/%s" % uri.replace("spotify:", "").replace(":", "/")


class NoProgress(object):

    def __init__(self, iterable):
        self.iterable = iterable

    def __enter__(self):
        return self

    def __iter__(self):
        return iter(self.iterable)

    def __exit__(self, exc_type, exc_val, exc_tb):
        return


class PlaylistGenerator(FileProcessor):

    def __init__(self, input, show_progress=False, lastfm_api_key=None):
        super(PlaylistGenerator, self).__init__(input=input, output=None)
        self.spotify = Spotify()
        self.show_progress = show_progress
        self.lastfm = LastFMAPI(api_key=lastfm_api_key)

    def _progress(self, iterable, **kwargs):
        if self.show_progress:
            kwargs.setdefault("show_pos", True)
            return click.progressbar(iterable, **kwargs)
        else:
            return NoProgress(iterable)

    def read_input_tracks(self):
        tracks = []

        with self._progress(self._read_lines(), label="parsing") as lines:
            for line in lines:
                if line.startswith("spotify:track:"):
                    tracks.append(SpotifyTrack(self.spotify.track(line)))
                elif " - " in line:
                    tracks.append(PseudoTrack(line, " - "))
                elif " / " in line:
                    tracks.append(PseudoTrack(line, " / "))
                else:
                    log.warn("Can't parse line: %s" % line)

        return tracks

    def youtube_match(self, tracks):
        youtube = YoutubeAPI()
        youtube_matcher = YoutubeMatcher(youtube)
        with self._progress(tracks, label="youtube") as track_iter:
            for track in track_iter:
                if not track.get("youtube"):
                    track["youtube"] = youtube_matcher.match_track(track)
        return tracks

    def deduplicate(self, tracks):
        out_tracks = []
        seen = set()
        for track in tracks:
            key = flatten("%s %s" % (track.get_artist_string(), track["name"]))
            if track["href"] in seen or key in seen:
                continue
            out_tracks.append(track)
            seen.add(track["href"])
            seen.add(key)
        return out_tracks

    def add_lastfm_tags(self, tracks, lastfm_api_key=None):
        lfm = self.lastfm
        if not lfm.api_key:  # pragma: no cover
            log.warn("Skipping Last.fm tags (no API key given)")
            return tracks

        with self._progress(tracks, label="last.fm") as track_iter:
            for track in track_iter:
                tags_counter = lfm.get_artists_tags_counter([a["name"] for a in track["artists"]])
                track["artist_tags"] = [t[0] for t in tags_counter.most_common(5)]
        return tracks

    def write_html(self, output_name, tracks):
        template_dir = os.path.join(os.path.dirname(__file__), "../templates")
        env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
        for tpl_name in ("cards", "table"):
            tpl = env.get_template("%s.jinja" % tpl_name)
            with codecs.open("%s-%s.html" % (output_name, tpl_name), "wb", encoding="UTF-8") as outf:
                outf.write(tpl.render(tracks=tracks))


@click.command("generate-playlist", short_help="Generate a playlist HTML file out of Spotify track URIs.")
@click.option("-i", "--input", required=True, help=u"Name of file containing spotify:track: URIs, one per line", metavar="FILENAME", type=click.File('rb'))
@click.option("-o", "--output-name", required=True, help=u"Base name for output data (cache and HTML)", metavar="BASENAME", type=click.Path())
@click.option("-p", "--progress/--no-progress", "show_progress", default=True, help="Show progress")
@click.option("-y", "--youtube/--no-youtube", "youtube", default=True, help="Fetch YouTube URLs")
@click.option("-l", "--lastfm/--no-lastfm", "lastfm", default=True, help="Fetch Last.fm tags")
@click.option("-d", "--dedupe/--no-dedupe", "dedupe", default=True, help="Deduplicate")
@click.option("--lastfm-api-key", default=None, help=u"Last.fm API key, for artist tag support", metavar="KEY")
def generate_playlist(input, output_name, show_progress, lastfm_api_key, lastfm, youtube, dedupe):  # pragma: no cover
    plg = PlaylistGenerator(input=input, show_progress=show_progress, lastfm_api_key=lastfm_api_key)
    tracks = plg.read_input_tracks()
    if dedupe:
        tracks = plg.deduplicate(tracks)

    if youtube:
        tracks = plg.youtube_match(tracks)

    if lastfm:
        tracks = plg.add_lastfm_tags(tracks)

    plg.write_html(output_name, tracks)
