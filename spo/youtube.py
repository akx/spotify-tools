# -- encoding: UTF-8 --
import os
import logging
from spo.cache import Cache
from googleapiclient.discovery import build as build_client


class YoutubeAPI(object):
    def __init__(self):
        self.cache = Cache("youtube_cache", 30 * 86400)
        self.log = logging.getLogger("YoutubeAPI")
        self.yt_client = build_client("youtube", "v3", developerKey=os.environ.get("GOOGLE_API_KEY"))

    def search(self, search_terms):
        key = "search:%s" % search_terms
        cached = self.cache.get(key)
        if cached:  # pragma: no cover
            self.log.debug("Using cached result for search %r" % search_terms)
            return cached
        self.log.info("Searching for %r" % search_terms)
        list_q = self.yt_client.search().list(
            q=search_terms,
            order="viewCount",
            part="snippet",
            type="video",
            maxResults=50
        )
        feed = list_q.execute()
        self.cache[key] = feed
        return feed
