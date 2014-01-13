import argparse
import requests, codecs, sys
from spo.tools import Tool


class AlbumListToSpotifyURLs(Tool):
	tool_name = "album-list-to-spotify"

	@classmethod
	def populate_parser(cls, parser):
		parser.add_argument("input", type=argparse.FileType("rb"), default="-", help=u"Name of file containing artist / album combinations, one per line")
		parser.add_argument("-o", "--output", type=argparse.FileType('wb'), default="-")

	def run(self, input, output, **kwargs):
		albums = []
		for line in codecs.EncodedFile(input, "UTF-8"):
			line = line.strip()
			if not line or line.startswith("#"):
				continue
			albums.append(line.replace("&amp;", "&"))

		output = codecs.EncodedFile(output, "UTF-8")

		for album in albums:
			q = album.replace(" - ", " ")
			resp = requests.get("http://ws.spotify.com/search/1/album.json", params={"q": q})
			resp.raise_for_status()
			data = resp.json()

			try:
				self.log.info("Found result for %r", q)
				spot = data["albums"][0]
				print >>output, "# + %r" % q
				print >>output, "# > %r, %r" % (spot["artists"][0]["name"], spot["name"])
				print >>output, "%s" % spot["href"]
			except (KeyError, IndexError):
				self.log.info("No result for %r", q)
				print >>output, "# - %r" % q
				continue
			print >>output

class SpotifyAlbumURLsToTrackURLs(Tool):
	tool_name = "spotify-albums-to-tracks"

	@classmethod
	def populate_parser(cls, parser):
		parser.add_argument("input", type=argparse.FileType("rb"), default="-", help=u"Name of file containing spotify:album: URIs, one per line")
		parser.add_argument("-o", "--output", type=argparse.FileType('wb'), default="-")

	def run(self, input, output, **kwargs):

		output = codecs.EncodedFile(output, "UTF-8")

		for line in codecs.EncodedFile(input, "UTF-8"):
			line = line.strip()
			if line.startswith("spotify:album:"):
				resp = requests.get("http://ws.spotify.com/lookup/1/.json", params={"uri": line, "extras": "track"})
				resp.raise_for_status()
				try:
					data = resp.json()["album"]
					print >>output, "# %s - %s (%s)" % (data["artist"], data["name"], data["href"])
					for track in data["tracks"]:
						print >>output, track["href"]
					print >>output
				except:
					print >>output, "# failed: %s" % line