import logging
import os
import pickle
import shutil

import util


def _get_path(namespace, key=None):
    ns_cache_path = os.path.join(util.get_root_fs(), 'cache', namespace)
    os.makedirs(ns_cache_path, exist_ok=True)
    if key:
        return os.path.join(str(ns_cache_path), f'{key}.pkl')
    return ns_cache_path


def get(namespace, key):
    try:
        with open(_get_path(namespace, f'{key.strip().lower()}'), 'rb') as f:
            value = pickle.load(f)
            logging.info(f'cache hit for {key} in namespace: {namespace}, with value: {value}')
            return value
    except FileNotFoundError:
        return None


def put(namespace, key, value):
    with open(_get_path(namespace, f'{key.strip().lower()}'), 'wb') as f:
        pickle.dump(value, f)


def clear(namespace):
    namespace_path = _get_path(namespace)
    if os.path.exists(namespace_path):
        shutil.rmtree(namespace_path)
        logging.info(f'cache for namespace {namespace} has been cleared.')
    else:
        logging.warning(f'cache for namespace {namespace} does not exist.')
