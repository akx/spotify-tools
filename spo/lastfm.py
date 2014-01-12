# -- encoding: UTF-8 --
import logging
from requests import Session
from spo.cache import Cache


class LastFMAPI(object):
	def __init__(self, api_key):
		self.session = Session()
		self.cache = Cache("spotify_cache", 24 * 86400)
		self.log = logging.getLogger("LastfmAPI")
		self.api_key = api_key


	def get_json(self, url, **kwargs):
		response = self.session.get(url, **kwargs)
		response.raise_for_status()
		return response.json()

	def get_artist_tags(self, artist):
		key = "artist tags %s" % artist
		tags = self.cache[key]
		if not tags:
			tags = self.get_json("http://ws.audioscrobbler.com/2.0/", params={
				"method": "artist.gettoptags",
				"artist": artist,
				"api_key": self.api_key,
				"format": "json"
			})
			self.cache[key] = tags
		return tags



