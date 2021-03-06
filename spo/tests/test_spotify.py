# -- encoding: UTF-8 --
import os, pytest
from StringIO import StringIO
from spo.tools.spotify_playlists_to_tracks import SpotifyPlaylistsToTracks
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


def test_playlists_to_tracks():
    if not os.getenv("SPOTIPY_CLIENT_ID"):
        pytest.skip("SPOTIPY_CLIENT_ID required")
    output_sio = StringIO()
    SpotifyPlaylistsToTracks(input=StringIO("spotify:user:spotify:playlist:3kjNcwrUClSp1Iatukq3TC"), output=output_sio).run()
    assert output_sio.getvalue().count("spotify:track:") > 5
