# -- encoding: UTF-8 --
from spo.youtube import YoutubeAPI
from spo.yt_matcher import YoutubeMatcher
from spo.spotify import Spotify


def test_youtube_match():
    youtube = YoutubeAPI()
    youtube.cache = {}  # Don't cache.
    youtube_matcher = YoutubeMatcher(youtube)
    track = Spotify().track("spotify:track:36c4JohayB9qd64eidQMBi")
    yt_track = youtube_matcher.match_track(track)
    assert "Daft Punk" in yt_track["title"]
