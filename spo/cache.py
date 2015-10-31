# -- encoding: UTF-8 --

import json
from sqlitedict import SqliteDict
import os
import string
import time
import unicodedata
import pickle
import functools

def _make_key(args, kwds):
    # h/t Python 3.4 functools
    key = args
    if kwds:
        key += ("\x00\x03",)
        for item in sorted(kwds.items()):
            key += item
    elif len(key) == 1 and type(key[0]) in {int, str, unicode, frozenset, type(None)}:
        return key[0]
    return tuple(key)

class Cache(object):

    def __init__(self, path, max_life):
        self.storage = SqliteDict("cache.sqlite3", tablename=path)
        self.max_life = int(max_life)

    def transform_key(self, key):
        return unicode(key)

    def put(self, key, value, life=0):
        expire = time.time() + (life or self.max_life)
        self._put_shelve(key, value, expire)

    def _put_shelve(self, key, value, expire):
        self.storage[self.transform_key(key)] = {"expire": expire, "value": value}

    def get(self, key, default=None):
        t_key = self.transform_key(key)
        expire = None
        value = default
        if t_key in self.storage:
            shelved = self.storage[t_key]
            value = shelved["value"]
            expire = shelved["expire"]

        if expire is not None and time.time() > expire:
            value = default

        return value

    def has(self, key):
        return (self.transform_key(key) in self.storage)

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        return self.put(key, value)

    def __contains__(self, item):
        return self.has(item)

    def cached(self, func):
        @functools.wraps(func)
        def cached_func(*args, **kwargs):
            cache_key = _make_key(args, kwargs)
            if cache_key not in self:
                self[cache_key] = value = func(*args, **kwargs)
            else:
                value = self[cache_key]
            return value
        return cached_func
