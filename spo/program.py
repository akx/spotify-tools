# -- encoding: UTF-8 --
import argparse
import logging

from spo.tools.playlist_gen import PlaylistGenerator
from spo.tools.album_list import AlbumListToSpotifyURLs, SpotifyAlbumURLsToTrackURLs

known_tools = [
	PlaylistGenerator,
    AlbumListToSpotifyURLs,
    SpotifyAlbumURLsToTrackURLs

]

class Program(object):
	def cmdline(self):
		ap = argparse.ArgumentParser()

		g = ap.add_argument_group("Logging")
		g.set_defaults(log_level=logging.WARN)
		g.add_argument("-d", "--debug", dest="log_level", action="store_const", const=logging.DEBUG, help=u"Logging level: debug")
		g.add_argument("-v", "--verbose", dest="log_level", action="store_const", const=logging.INFO, help=u"Logging level: info")

		subparsers = ap.add_subparsers()

		for tool_class in known_tools:
			if tool_class.tool_name:
				subparser = subparsers.add_parser(tool_class.tool_name)
				subparser.set_defaults(tool_class=tool_class)
				tool_class.populate_parser(subparser)

		args = ap.parse_args()

		log_level = args.__dict__.pop("log_level")
		logging.basicConfig(level=log_level)
		tool_class = args.__dict__.pop("tool_class")

		tool = tool_class()
		return tool.run(**vars(args))