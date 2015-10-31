# -- encoding: UTF-8 --
import logging
import re
from spo.cache import Cache
from spo.util import flattened_levenshtein


class YoutubeMatcher(object):

    def __init__(self, youtube_api):
        self.log = logging.getLogger("YoutubeMatcher")
        self.youtube_api = youtube_api
        self.cache = Cache("youtube_matcher", max_life=60 * 60 * 24 * 7)

    def cleanup_title(self, name):
        name = name.replace("Original Mix", "")
        name = re.sub("\(milan.+\)", "", name, flags=re.I)
        name = re.sub("[() -]+", " ", name)
        return name.strip()

    def cleanup_artist(self, name):
        name = re.sub("^the\s+", "", name, flags=re.I)
        name = name.replace("unreleased", "")
        name = re.sub("[() -]+", " ", name)
        return name.strip()

    def match_track(self, track):
        artist_variations = []
        for artist in track["artists"]:
            artist_name = artist["name"]
            artist_variations.append(self.cleanup_artist(artist_name))
            for artist in artist_name.split("&"):
                artist_variations.append(self.cleanup_artist(artist))
        title = track["name"]
        try:
            length = float(track["length"])
        except KeyError:
            length = None

        termses = []

        for artist in artist_variations:
            terms = "%s %s" % (artist, self.cleanup_title(title))
            if terms not in termses:
                termses.append(terms)

        for search_terms in termses:
            ents = self.find_best_matches(search_terms, length)
            if ents:
                self.log.info("Got match for %r: %r" % (search_terms, ents[0]["url"]))
                return ents[0]
            else:
                self.log.info("No results for %r..." % search_terms)
        return None

    def _score_single_entry(self, ent, expected_length, max_views, search_terms):
        score = 0
        score += ent.get("position", 0) * 0.2
        score += flattened_levenshtein(search_terms.lower(), ent["title"].lower())
        if ent["length"] is not None and expected_length:
            score += abs(expected_length - ent["length"])
        if ent["rating"] < 0:
            score *= -ent["rating"]
        if "live" in ent["title"].lower():
            score *= 1.2
        if "cover" in ent["title"].lower():
            score *= 2
        if max_views > 0:
            views = (ent["views"] / max_views)
        else:
            views = 0
        score += (score * 0.3) * 1.0 - views
        return score

    def find_best_matches(self, search_terms, expected_length):
        ents = []
        feed = self.youtube_api.search(search_terms)
        for position, entry in enumerate(feed["items"]):
            ent = {
                "title": entry["snippet"]["title"],
                "length": None,  # Unavailable, alas
                "url": "https://youtube.com/watch?v=" + entry["id"]["videoId"],
            }
            try:
                ent["views"] = float(entry.statistics.view_count)
            except:
                ent["views"] = 0
            try:
                ent["rating"] = float(entry.rating.average) - 2.5
            except:
                ent["rating"] = 0
            ent["position"] = position
            ents.append(ent)

        if ents:

            max_views = max(e["views"] for e in ents)

            for ent in ents:
                ent["score"] = self._score_single_entry(ent, expected_length, max_views, search_terms)

            ents.sort(key=lambda ent: ent["score"])

        return ents
