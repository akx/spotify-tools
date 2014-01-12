# -- encoding: UTF-8 --

import argparse
from collections import Counter
import logging, codecs
import os
from pickle import dump, load
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from spo.lastfm import LastFMAPI

from spo.spotify import SpotifyAPI
from spo.youtube import YoutubeAPI
from spo.yt_matcher import YoutubeMatcher


class Program(object):
	def __init__(self):
		self.log = logging.getLogger("Splist")

	def read_and_match_file(self, url_file):
		tracks = []
		sa = SpotifyAPI()
		yt = YoutubeAPI()
		ytm = YoutubeMatcher(yt)

		for line in file(url_file, "rb"):
			line = line.strip()
			if line.startswith("spotify:track:"):
				tracks.append(sa.search_by_uri(line))

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
			if track["href"] in seen:
				continue
			out_tracks.append(track)
			seen.add(track["href"])
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


	def cmdline(self):
		ap = argparse.ArgumentParser()
		ap.add_argument("input_list", help=u"Name of file containing spotify:track: URIs, one per line")
		ap.add_argument("-o", "--output-name", required=True, help=u"Base name for output data (cache and HTML)")
		ap.add_argument("-c", "--use-cache", action="store_true", help=u"Use generated results cache file (speeds up subsequent runs, but changes to input list are not recorded)")
		ap.add_argument("--lastfm-api-key", help=u"Last.fm API key, for artist tag support")
		g = ap.add_argument_group("Logging")
		g.add_argument("-d", "--debug", action="store_true", help=u"Logging level: debug")
		g.add_argument("-v", "--verbose", action="store_true", help=u"Logging level: verbose")

		args = ap.parse_args()
		if args.debug:
			logging.basicConfig(level=logging.DEBUG)
		elif args.verbose:
			logging.basicConfig(level=logging.INFO)
		else:
			logging.basicConfig(level=logging.WARN)

		return self.run(args.input_list, args.output_name, args.use_cache, args.lastfm_api_key)

	def run(self, input_list, output_name, use_cache=False, lastfm_api_key=None):
		cache_file = "%s.cache" % output_name

		if use_cache:
			tracks = self.read_from_cache(cache_file)
		else:
			tracks = self.read_into_cache(input_list, cache_file)

		tracks = self.deduplicate(tracks)

		if lastfm_api_key:
			self.add_tags(lastfm_api_key, tracks)
		else:
			self.log.warn("Skipping tags (no API key given)")


		for track in tracks:
			track["artist"] = ", ".join(a["name"] for a in track["artists"])
			track["open_spotify_url"] = track["href"].replace(":", "/").replace("spotify/", "http://open.spotify.com/")

		tracks.sort(key=lambda t:t["name"])

		template_dir = os.path.join(os.path.dirname(__file__), "templates")
		env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
		for tpl_name in ("cards", "table"):
			tpl = env.get_template("%s.jinja" % tpl_name)
			with codecs.open("%s-%s.html" % (output_name, tpl_name), "wb", encoding="UTF-8") as outf:
				outf.write(tpl.render(tracks=tracks))
