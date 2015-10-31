# -- encoding: UTF-8 --
from __future__ import print_function
import click
from spo.spotify import Spotify
from spo.util import batch
import re

TRACK_RE = re.compile("^(?:https://api.spotify.com/v1/tracks/|spotify:track:)(.+?)$")

@click.command(u"spotify-write-pl", short_help="Create a Spotify playlist based on a list of track URIs.")
@click.argument(u"input", type=click.File("rb"), required=True)
@click.option(u"--name", required=False)
@click.option(u"--playlist-id", required=False)
def spotify_write_playlist(input, name, playlist_id):  # pragma: no cover
    if not (name or playlist_id):
        raise click.UsageError(u"Need either name or id")

    track_ids = get_track_ids(input)

    sp = Spotify(auth=True)
    if name:
        playlist = sp.user_playlist_create(sp.auth_username, name, public=False)
        print("Created new playlist with ID: %s" % playlist["id"])
    else:
        playlist = sp.user_playlist(sp.auth_username, playlist_id)

    name = playlist["name"]
    playlist_id = playlist["id"]
    print(u"Writing %d tracks to playlist: %s" % (len(track_ids), name))
    n_written = 0
    for track_batch in batch(track_ids, 90):
        sp.user_playlist_add_tracks(sp.auth_username, playlist_id, track_batch)
        n_written += len(track_batch)
        print(u"%d / %d tracks done" % (n_written, len(track_ids)))


def get_track_ids(input):
    track_ids = []
    for line in input:
        line = line.strip()
        m = TRACK_RE.match(line)
        if m:
            track_ids.append(m.group(1))
    return track_ids
