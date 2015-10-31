# -- encoding: UTF-8 --
import os
from spo.cache import Cache
from spotipy.client import Spotify as _Spotify, SpotifyException

SpotifyException = SpotifyException


class Spotify(_Spotify):
    auth_token = None
    auth_username = os.environ.get("SPOTIFY_USERNAME")

    def __init__(self, auth=None):
        if auth is True:
            from spotipy.util import prompt_for_user_token
            auth = prompt_for_user_token(self.auth_username, scope=" ".join([
                "playlist-read-private",
                "playlist-read-collaborative",
                "playlist-modify-public",
                "playlist-modify-private",
                "user-library-read",
                "user-library-modify"
            ]))
        if not auth:
            auth = self.auth_token
        super(Spotify, self).__init__(auth=auth)
        self.cache = Cache("spotify_cache", max_life=86400 * 7)

    def _cached(self, cache_key, getter):
        if cache_key not in self.cache:
            value = getter()
            self.cache[cache_key] = value
        else:
            value = self.cache[cache_key]
        return value

    def track(self, track_id):
        return self._cached("track %s" % track_id, lambda: super(Spotify, self).track(track_id))

    def album(self, album_id):
        return self._cached("album %s" % album_id, lambda: super(Spotify, self).album(album_id))

    def search(self, **kwargs):
        return self.cache.cached(super(Spotify, self).search)(**kwargs)
