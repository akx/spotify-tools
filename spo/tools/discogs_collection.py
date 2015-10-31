# -- encoding: UTF-8 --
import re
import click
import sys
import logging
from spo.discogs import get_discogs_collection

@click.command(u"get-discogs-collection-albums", short_help="Get the names of albums in a Discogs user collection.")
@click.argument(u"username", required=True)
@click.option(u"--output", u"-o", type=click.File("w", encoding="utf8"), default=sys.stdout)
def get_discogs_collection_albums(username, output):
    collection = get_discogs_collection(username)
    lines = set()
    for release in collection:
        release = release["basic_information"]
        artist = re.sub(r"\s+\(\d+\)$", "", release["artists"][0]["name"])
        title = release["title"]
        lines.add(u"%s - %s" % (artist, title))
    output.write("\n".join(sorted(lines)))
