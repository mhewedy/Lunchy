import os
import random
import time
from typing import Any
from typing import Callable

from telegram import Update
from telegram.ext import ContextTypes


def retry_function(func: Callable, retries: int = 5, delay: int = 1, *args, **kwargs) -> Any:
    attempts = 0
    while attempts < retries:
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            attempts += 1
            print(f"Attempt calling {func} #{attempts} failed with error: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception(f"Function {func} failed after {retries} attempts")


def current_user(update: Update) -> (int, str):
    return update.effective_user.id, update.effective_user.full_name


async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    administrators = await context.bot.get_chat_administrators(update.message.chat_id)

    for admin in administrators:
        if admin.user.id == update.effective_user.id:
            return True

    return False


def get_congrats_msg():
    return random.choice([
        "صاحب الحظ السعيد اليوم هو",
        "يا هناك يا سعدك يا",
        "اليوم يومك النهارده يا",
        "مبروك عليك ... هتطلب لنا اليوم يا"
    ])


def get_root_fs():
    return os.getenv('VOLUME_ROOT_FS', '/tmp') + '/lunchy'
