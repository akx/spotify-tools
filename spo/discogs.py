# -- encoding: UTF-8 --
import requests
from spo.cache import Cache
import logging

cache = Cache("discogs_cache", max_life=86400)


@cache.cached
def get_discogs_collection(username):
    params = {"per_page": 100, "page": 1}
    releases = []
    sess = requests.session()
    n_pages = "???"
    while True:
        logging.info("Downloading page %d/%s of Discogs collection" % (params["page"], n_pages))
        data = sess.get(
            "https://api.discogs.com/users/%s/collection/folders/0/releases" % username,
            params=params,
            headers={"User-Agent": "+spotify-tools/0.1"}
        ).json()
        page_releases = data.get("releases")
        if not page_releases:
            break
        n_pages = data["pagination"]["pages"]
        releases.extend(page_releases)
        params["page"] += 1
    logging.info("%s: %d releases in collection." % (username, len(releases)))
    return releases
