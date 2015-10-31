# spotify-tools

A collection of tools to work with various music services, mostly centered around Spotify.

This tool is not affiliated with Spotify, YouTube, Discogs, Last.fm or any other service whose
API is in use.  (Thanks for the APIs though. <3)

## Installation

The usual. This assumes you have a working Python 2.7 ecosystem on your machine.

### Linux

```
virtualenv venv
venv/bin/activate
pip install -r requirements.txt
```

### Windows

```
virtualenv venv
venv\scripts\activate
pip install -r requirements.txt
```


## How to...

### Generate a Spotify playlist of your Discogs collection

```
python sp-tool.py get-discogs-collection-albums MY_DISCOGS_USERNAME -o discogs.txt
python sp-tool.py spotify-search-albums discogs.txt -o album-urls.txt
python sp-tool.py spotify-albums-to-tracks album-urls.txt -o track-urls.txt
python sp-tool.py --spotify-username MY_SPOTIFY_USERNAME spotify-write-pl --name Discogs track-urls.txt
```

The last invocation will require a [Spotify Dev App ID](https://developer.spotify.com/).
