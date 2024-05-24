import logging
import os
import pickle

import util

root_fs_cache = util.get_root_fs() + '/cache'


def _cache_path(namespace, key):
    cache_namespace = root_fs_cache + '/' + namespace
    os.makedirs(cache_namespace, exist_ok=True)
    return os.path.join(cache_namespace, f'{key}.pkl')


def get(namespace, key):
    try:
        with open(_cache_path(namespace, f'{key.strip().lower()}'), 'rb') as f:
            value = pickle.load(f)
            logging.info(f'cache hit for {key} in namespace: {namespace}, with value: {value}')
            return value
    except FileNotFoundError:
        return None


def put(namespace, key, value):
    with open(_cache_path(namespace, f'{key.strip().lower()}'), 'wb') as f:
        pickle.dump(value, f)
