# -- encoding: UTF-8 --

import json
import os
import string
import time
import unicodedata
import pickle


class Cache(object):

    def __init__(self, path, max_life):
        self.path = path
        if not os.path.isdir(self.path):
            os.makedirs(self.path)
        self.max_life = int(max_life)

    def transform_key(self, key):
        key = unicode(key)
        key = unicodedata.normalize("NFKD", key).encode("ascii", "ignore")
        key = "".join((c if c in string.ascii_letters + string.digits else "_") for c in key)
        key = os.path.join(self.path, key)
        return key

    def put(self, key, value, life=0):
        expire = time.time() + (life or self.max_life)
        value = [expire, value]
        try:
            data = json.dumps(value)
        except TypeError:
            data = pickle.dumps(value, -1)
        with file(self.transform_key(key), "wb") as fp:
            fp.write(data)

    def get(self, key, default=None):
        key = self.transform_key(key)
        if os.path.isfile(key):
            with file(key, "rb") as fp:
                k = fp.read(1)
                fp.seek(0)
                if k in "[{":
                    expires, value = json.load(fp)
                else:
                    expires, value = pickle.load(fp)
                if time.time() <= expires:
                    return value
                else:
                    return default
        return default

    def has(self, key):
        return os.path.isfile(self.transform_key(key))

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        return self.put(key, value)

    def __contains__(self, item):
        return self.has(item)
