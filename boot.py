import logging
import os

import dateutil.parser
from telegram.ext import Application
from telegram.ext import CommandHandler, MessageHandler, filters

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging = logging.getLogger(__name__)

CHAT_ID = os.getenv("CHAT_ID", -4201961515)
logging.info(f'G_CHAT_ID: {CHAT_ID}')

cmds = []
application = Application.builder().token(os.getenv("BOT_TOKEN")).build()


def command(name=None, desc=None, text=False):
    def wrapper(func):
        if name: cmds.append((name, desc))

        def wrapped_func(*args, **kwargs):
            global CHAT_ID
            logging.info(f"invoking command: {func.__name__}")

            (update, _) = args
            CHAT_ID = update.edited_message.chat_id if update.edited_message else update.message.chat_id
            logging.info(f'setting g_chat_id to: {CHAT_ID}')

            return func(*args, **kwargs)

        if name: logging.info(f"declaring command: {name}")
        if text:
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, wrapped_func))
        else:
            application.add_handler(CommandHandler(name, wrapped_func))
        return wrapped_func

    return wrapper


def job(time, enabled=True):
    def wrapper(func):
        if enabled:
            logging.info(f'scheduling {func.__name__} at: {dateutil.parser.parse(time).time()} UTC')

        def wrapped_func(*args, **kwargs):
            logging.info(f"invoking job: {func.__name__}")
            new_args = args + (CHAT_ID,)
            result = func(*new_args, **kwargs)
            return result

        if enabled:
            wrapped_func.__name__ = f'w/{func.__name__}'
            application.job_queue.run_daily(wrapped_func, time=dateutil.parser.parse(time).time())
        return wrapped_func

    return wrapper
