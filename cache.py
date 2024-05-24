import logging
import os
import pickle
import shutil

import util

root_fs_cache = util.get_root_fs() + '/cache'


def _cache_path(namespace, key=None):
    cache_namespace = root_fs_cache + '/' + namespace
    os.makedirs(cache_namespace, exist_ok=True)
    if key:
        return os.path.join(cache_namespace, f'{key}.pkl')
    else:
        return cache_namespace


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


def clean(namespace):
    cache_namespace = _cache_path(namespace)
    if os.path.exists(cache_namespace):
        shutil.rmtree(cache_namespace)
        logging.info(f'Cache for namespace {namespace} has been cleaned.')
    else:
        logging.warning(f'Cache for namespace {namespace} does not exist.')
