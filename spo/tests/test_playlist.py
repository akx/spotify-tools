# -- encoding: UTF-8 --
from StringIO import StringIO
import time
import os
from spo.tools.playlist_gen import PlaylistGenerator

PLAYLIST_INPUT_CONTENT = """
spotify:track:30V66R2gD8g4g93cBlru3r
spotify:track:3aVdIgxZ3ci1ayhQeoOgUn
spotify:track:7EvdU8Ak83BbxjPJLrom7I
# Hi mom
spotify:track:4ccIlWJ2R0FAI8bDyFdMTu
spotify:track:2daaKVdpmEoWWm2FPQCJsi
spotify:track:0dEIca2nhcxDUV8C5QkPYb
spotify:track:3ctALmweZBapfBdFiIVpji
spotify:track:3ctALmweZBapfBdFiIVpji
Daft Punk - Doin' It Right
spotify:track:3ctALmweZBapfBdFiIVpji
spotify:track:3ctALmweZBapfBdFiIVpji
spotify:track:7Bxv0WL7UC6WwQpk9TzdMJ
spotify:track:2cGxRwrMyEAp8dEbuZaVv6
Metro Area / Caught Up
spotify:track:0oks4FnzhNp5QPTZtoet7c
spotify:track:5CMjjywI0eZMixPeqNd75R
ferskhfsdhjk plerk
"""


def test_playlist():
    if not os.path.isdir("test_output"):
        os.mkdir("test_output")
    plg = PlaylistGenerator(input=StringIO(PLAYLIST_INPUT_CONTENT))
    tracks = plg.read_input_tracks()
    assert any(t.get("uri") == "spotify:track:5CMjjywI0eZMixPeqNd75R" for t in tracks)
    assert len(plg.deduplicate(tracks)) < len(tracks)
    tracks = plg.youtube_match(tracks)
    assert all(t.get("youtube") for t in tracks)
    if plg.lastfm.api_key:
        lfm_tracks = plg.add_lastfm_tags(tracks)
        assert any(t.get("artist_tags") for t in lfm_tracks)
    plg.write_html("test_output/%d" % time.time(), tracks)
