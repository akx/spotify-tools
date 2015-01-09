# -- encoding: UTF-8 --

import json
import shelve
import os
import string
import time
import unicodedata
import pickle


class Cache(object):

    def __init__(self, path, max_life):
        self.path = path
        self.shelf = shelve.open("%s.shelve" % self.path)
        self.max_life = int(max_life)

    def transform_key(self, key):
        key = unicode(key)
        key = unicodedata.normalize("NFKD", key).encode("ascii", "ignore")
        key = "".join((c if c in string.ascii_letters + string.digits else "_") for c in key)
        key = os.path.join(self.path, key)
        return key

    def put(self, key, value, life=0):
        expire = time.time() + (life or self.max_life)
        self._put_shelve(key, value, expire)

    def _put_shelve(self, key, value, expire):
        self.shelf[self.transform_key(key)] = {"expire": expire, "value": value}

    def get(self, key, default=None):
        t_key = self.transform_key(key)
        expire = None
        value = default
        if t_key in self.shelf:
            shelved = self.shelf[t_key]
            value = shelved["value"]
            expire = shelved["expire"]

        if expire is not None and time.time() > expire:
            value = default

        return value

    def has(self, key):
        return os.path.isfile(self.transform_key(key))

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        return self.put(key, value)

    def __contains__(self, item):
        return self.has(item)
