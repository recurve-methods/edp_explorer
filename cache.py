import pickle
import hashlib
import os
import shutil
import logging
import pandas as pd
import numpy as np
import simplejson as json

logger = logging.getLogger(__name__)


def digest(x, n=16):
    x = str(x)
    x = x.encode()
    return hashlib.sha224(x).hexdigest()[0 : n - 1]


def mkdirs(path):
    if os.path.dirname(path) != "":
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
    return path


class Cacheable(object):
    cache_dir = None

    def __init__(self, cache_location=".", cache_name=".cache_recurve"):
        cache_dir = os.path.join(cache_location, cache_name)
        logging.debug(f"Initializing cache at {cache_dir}")        
        mkdirs(cache_dir)
        self.cache_dir = cache_dir

    def _fail_if_not_init(self):
        if self.cache_dir is None:
            raise ValueError("Please call Cacheable.__init__() to initialize cache")

    def clear_cache(self):
        self._fail_if_not_init()
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)

    def _cache_path(self, path):
        self._fail_if_not_init()
        return mkdirs(os.path.join(self.cache_dir, path))

    def make_cache_key(self, object_to_serialize):
        """ Convert an object to a 16-bit string digest representation."""
        return digest(object_to_serialize)

    def cache_func(self, func, key):
        try:
        	path = self._cache_path(key)
        	if not os.path.exists(path):
        		obj = func()
        		with open(path, 'wb') as f:
        			pickle.dump(obj, f)
        	with open(path, 'rb') as f:
        		return pickle.load(f)
        except Exception as e:
            return func()

