import logging
from functools import wraps

import envars


def command(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"invoking command: {func.__name__}")

        (update, _) = args
        envars.CHAT_ID = update.edited_message.chat_id if update.edited_message else update.message.chat_id
        logging.info(f'setting g_chat_id to: {envars.CHAT_ID}')

        result = func(*args, **kwargs)
        return result

    return wrapper


def job(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"invoking job: {func.__name__}")
        new_args = args + (envars.CHAT_ID,)
        result = func(*new_args, **kwargs)
        return result

    return wrapper
