# -- encoding: UTF-8 --
import pytest
from spo.lastfm import LastFMAPI


def test_last_fm():
    lfm = LastFMAPI(api_key=None)
    if not lfm.api_key:  # pragma: no cover
        pytest.skip("Unable to test Last.fm without API key")
    lfm.cache = {}  # Never cache
    assert "rock" in lfm.get_artists_tags_counter(["The Beatles"])
    assert not lfm.get_artists_tags_counter(["whsdjfghdsaf9h4werujesfdiogmxc"])
