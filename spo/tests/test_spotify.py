# -- encoding: UTF-8 --
from StringIO import StringIO
from spo.tools.spotify_search import ListToSpotifyURLs
from spo.tools.spotify_albums_to_tracks import SpotifyAlbumURLsToTrackURLs

ALBUM_SEARCH_FILE = """
daft punk random access memories
wharrgarbl notfound
# totally a comment
; this too
"""


def test_album_search():
    output_sio = StringIO()
    ListToSpotifyURLs(mode="album", input=StringIO(ALBUM_SEARCH_FILE), output=output_sio).run()
    assert "4m2880jivSbbyEGAKfITCa" in output_sio.getvalue()
    assert "totally a comment" not in output_sio.getvalue()


def test_track_search():
    output_sio = StringIO()
    ListToSpotifyURLs(mode="track", input=StringIO("daft punk doin it right\nwharrgarbl notfound"), output=output_sio).run()
    assert "36c4JohayB9qd64eidQMBi" in output_sio.getvalue()


def test_album_to_tracks():
    output_sio = StringIO()
    SpotifyAlbumURLsToTrackURLs(input=StringIO("spotify:album:4m2880jivSbbyEGAKfITCa\nspotify:album:thisaintanuri"), output=output_sio).run()
    assert "Random Access" in output_sio.getvalue()  # Got the title"
    assert "36c4JohayB9qd64eidQMBi" in output_sio.getvalue()  # Got 'Doin' it right'"
