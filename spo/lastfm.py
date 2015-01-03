# -- encoding: UTF-8 --
from collections import Counter
import logging
import os
from requests import Session
from spo.cache import Cache


class LastFMAPI(object):

    def __init__(self, api_key):
        self.session = Session()
        self.cache = Cache("lastfm_cache", 24 * 86400)
        self.log = logging.getLogger("LastfmAPI")
        self.api_key = api_key or os.environ.get("LASTFM_API_KEY")

    def get_json(self, url, **kwargs):
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_artist_tags_raw(self, artist):
        key = "artist tags %s" % artist
        tags = self.cache.get(key)
        if tags is None:
            tags = self.get_json("http://ws.audioscrobbler.com/2.0/", params={
                "method": "artist.gettoptags",
                "artist": artist,
                "api_key": self.api_key,
                "format": "json"
            })
            self.cache[key] = tags
        return tags

    def get_artists_tags_counter(self, artists):
        if isinstance(artists, basestring):
            artists = [artists]
        tags = Counter()
        for artist in artists:
            data = self.get_artist_tags_raw(artist)

            try:
                tag_list = data["toptags"]["tag"]
            except KeyError:
                continue

            if isinstance(tag_list, dict):  # pragma: no cover
                tag_list = [tag_list]

            for tag in tag_list:
                words = [tag["name"].lower()]
                for word in words:
                    tags[word] += int(tag["count"]) / float(len(words))
        return tags
