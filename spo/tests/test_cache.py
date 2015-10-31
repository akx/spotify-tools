# -- encoding: UTF-8 --
from spo.cache import SqliteDict, Cache


def test_sqlitedict():
    sd = SqliteDict(":memory:", "foo")
    value = {"bar": "quux"}
    sd["foo"] = value
    assert sd["foo"] == value
    assert not ("bar" in sd)
    assert sd.get("foo") == value
    assert sd.get("bar", default=3) == 3
    del sd["foo"]
    assert not sd.get("foo")


def test_cache():
    cache = Cache("fee", 1, filename=":memory:")
    cache["foo"] = "bar"
    assert "foo" in cache
    assert cache.get("foo") == "bar"
