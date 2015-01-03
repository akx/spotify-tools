# -- encoding: UTF-8 --
import logging
from gdata.youtube.service import YouTubeService, YouTubeVideoQuery
from spo.cache import Cache


class YoutubeAPI(object):

    def __init__(self):
        self.cache = Cache("youtube_cache", 7 * 86400)
        self.log = logging.getLogger("YoutubeAPI")
        self.yt_service = YouTubeService()

    def search(self, search_terms):
        key = "search:%s" % search_terms
        cached = self.cache.get(key)
        if cached:  # pragma: no cover
            self.log.debug("Using cached result for search %r" % search_terms)
            return cached

        query = YouTubeVideoQuery()
        query.vq = search_terms.encode("UTF-8")
        query.orderby = 'viewCount'
        query.racy = 'include'
        query.max_results = 50
        self.log.info("Searching for %r" % search_terms)
        feed = self.yt_service.YouTubeQuery(query)
        self.cache[key] = feed
        return feed
