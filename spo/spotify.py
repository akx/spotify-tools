# -- encoding: UTF-8 --
import logging

from requests import Session
from spo.cache import Cache
from spo.util import peel


def peel_info(obj):
	if isinstance(obj, dict) and "info" in obj:
		obj = obj.copy()
		info = obj.pop("info", {})
		obj = peel(obj)
		obj["_info"] = info
	else:
		obj = peel(obj)
	return obj

class SpotifyAPI(object):
	def __init__(self):
		self.session = Session()
		self.cache = Cache("spotify_cache", 24 * 86400)
		self.log = logging.getLogger("SpotifyAPI")

	def get_json(self, url, **kwargs):
		response = self.session.get(url, **kwargs)
		response.raise_for_status()
		return response.json()

	def search_by_uri(self, uri):
		value = self.cache.get(uri)
		if value is None:
			self.log.info("Querying for URI %r" % uri)
			value = peel_info(self.get_json("http://ws.spotify.com/lookup/1/.json", params={"uri": uri}))
			self.cache[uri] = value
		else:
			self.log.debug("Using cached result for %r" % uri)
		return value