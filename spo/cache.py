# -- encoding: UTF-8 --

import json
import os
import string
import time
import unicodedata
import cPickle as pickle
import functools
import sqlite3


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


class SqliteDict(object):
    def __init__(self, path, tablename):
        self.path = path
        self.tablename = tablename
        self.conn = sqlite3.connect(path, isolation_level=None)
        self.conn.execute("CREATE TABLE IF NOT EXISTS %s (key TEXT PRIMARY KEY, value BLOB)" % self.tablename)
        self.conn.commit()

    def __contains__(self, key):
        key = unicode(key)
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM %s WHERE key = ?" % self.tablename, (key,))
        try:
            next(cur)[0]
            return True
        except StopIteration:
            return False

    def __getitem__(self, key):
        key = unicode(key)
        cur = self.conn.cursor()
        cur.execute("SELECT value FROM %s WHERE key = ?" % self.tablename, (key,))
        try:
            return self._decode(next(cur)[0])
        except StopIteration:
            raise KeyError(key)

    def __setitem__(self, key, value):
        key = unicode(key)
        cur = self.conn.cursor()
        cur.execute("REPLACE INTO %s (key, value) VALUES (?,?)" % self.tablename, (key, self._encode(value)))
        self.conn.commit()

    def __delitem__(self, key):
        cur = self.conn.cursor()
        self.conn.execute("DELETE FROM %s WHERE key = ?" % self.tablename, (key,))

    def _encode(self, obj):
        return sqlite3.Binary(pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL))

    def _decode(self, obj):
        return pickle.loads(bytes(obj))

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


class Cache(object):
    def __init__(self, namespace, max_life, filename="cache.sqlite3"):
        self.storage = SqliteDict(filename, tablename=namespace)
        self.max_life = int(max_life)

    def put(self, key, value, life=0):
        expire = time.time() + (life or self.max_life)
        self.storage[key] = {"expire": expire, "value": value}

    def get(self, key, default=None):
        expire = None
        value = default
        try:
            shelved = self.storage[key]
            value = shelved["value"]
            expire = shelved["expire"]
            if expire is not None and time.time() > expire:
                value = default
        except KeyError:
            return default
        return value

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        return self.put(key, value)

    def __contains__(self, item):
        return item in self.storage

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
