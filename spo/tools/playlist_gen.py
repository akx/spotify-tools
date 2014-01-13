# -- encoding: UTF-8 --

from collections import Counter
import hashlib
import codecs
import os
from pickle import dump, load
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from spo.lastfm import LastFMAPI

from spo.spotify import SpotifyAPI
from spo.tools import Tool
from spo.util import flatten
from spo.youtube import YoutubeAPI
from spo.yt_matcher import YoutubeMatcher


class PseudoTrack(dict):
	def __init__(self, string):
		artist, title = string.split(" - ", 1)
		self["artists"] = [{"name": artist}]
		self["name"] = title
		self["href"] = "pseudo:%s" % hashlib.md5(string.encode("UTF-8")).hexdigest()


class PlaylistGenerator(Tool):
	tool_name = "playlist-gen"

	@classmethod
	def populate_parser(cls, parser):
		parser.add_argument("input_list", help=u"Name of file containing spotify:track: URIs, one per line")
		parser.add_argument("-o", "--output-name", required=True, help=u"Base name for output data (cache and HTML)")
		parser.add_argument("-c", "--use-cache", action="store_true", help=u"Use generated results cache file (speeds up subsequent runs, but changes to input list are not recorded)")
		parser.add_argument("--lastfm-api-key", help=u"Last.fm API key, for artist tag support")

	def read_and_match_file(self, url_file):
		tracks = []
		sa = SpotifyAPI()
		yt = YoutubeAPI()
		ytm = YoutubeMatcher(yt)

		for line in codecs.open(url_file, "rb", encoding="UTF-8"):
			line = line.strip()
			if not line or line.startswith(";") or line.startswith("#"):
				continue
			if line.startswith("spotify:track:"):
				tracks.append(sa.search_by_uri(line))
			elif " - " in line:
				tracks.append(PseudoTrack(line))


		for track in tracks:
			track["youtube"] = ytm.match_track(track)

		return tracks

	def read_into_cache(self, input_list, cache_file):
		tracks = self.read_and_match_file(input_list)

		with file(cache_file, "wb") as outf:
			dump(tracks, outf, -1)
		return tracks

	def read_from_cache(self, cache_file):
		return load(file(cache_file, "rb"))

	def deduplicate(self, tracks):
		out_tracks = []
		seen = set()
		for track in tracks:
			key = flatten("%s %s" % (track["artist"], track["name"]))
			if track["href"] in seen or key in seen:
				continue
			out_tracks.append(track)
			seen.add(track["href"])
			seen.add(key)
		return out_tracks


	def add_tags(self, lastfm_api_key, tracks):
		lfm = LastFMAPI(lastfm_api_key)
		for track in tracks:
			tags = Counter()
			for a in track["artists"]:
				data = lfm.get_artist_tags(a["name"])
				try:
					tag_list = data["toptags"]["tag"]
					if isinstance(tag_list, dict):
						tag_list = [tag_list]
					for tag in tag_list:
						words = [tag["name"].lower()]
						for word in words:
							tags[word] += int(tag["count"]) / float(len(words))
				except KeyError:
					pass

			track["artist_tags"] = [t[0] for t in tags.most_common(5)]


	def run(self, input_list, output_name, use_cache=False, lastfm_api_key=None):
		cache_file = "%s.cache" % output_name

		if use_cache:
			tracks = self.read_from_cache(cache_file)
		else:
			tracks = self.read_into_cache(input_list, cache_file)


		if lastfm_api_key:
			self.add_tags(lastfm_api_key, tracks)
		else:
			self.log.warn("Skipping tags (no API key given)")


		for track in tracks:
			track["artist"] = ", ".join(a["name"] for a in track["artists"])
			if "spotify" in track["href"]:
				track["open_spotify_url"] = track["href"].replace(":", "/").replace("spotify/", "http://open.spotify.com/")
			else:
				track["open_spotify_url"] = None

		tracks = self.deduplicate(tracks)
		tracks.sort(key=lambda t:t["name"])

		template_dir = os.path.join(os.path.dirname(__file__), "../templates")
		env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
		for tpl_name in ("cards", "table"):
			tpl = env.get_template("%s.jinja" % tpl_name)
			with codecs.open("%s-%s.html" % (output_name, tpl_name), "wb", encoding="UTF-8") as outf:
				outf.write(tpl.render(tracks=tracks))
