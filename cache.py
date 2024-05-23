import logging

import diskcache

import util

cache = diskcache.Cache(util.get_root_fs() + '/cache')


def put(namespace, key: str, value):
    cache.set(f'{namespace}:{key.strip().lower()}', value)


def get(namespace, key: str):
    result = cache.get(f'{namespace}:{key.strip().lower()}')
    if result is not None:
        logging.info(f'cache hit for {namespace}:{key} -> {result}')
        return result
