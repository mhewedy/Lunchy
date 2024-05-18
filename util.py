import logging
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


class UserSelector:
    def __init__(self):
        self.history = []
        self.selection_gap = 2

    def select(self, users):
        if not users:
            raise ValueError('users list should not be empty')

        uniq_len = len(list(set(users)))
        excluded_users = self.history[
                         len(self.history) - (uniq_len - 1 if uniq_len <= self.selection_gap else self.selection_gap):
                         ]

        selected = random.choice(users)

        if selected in excluded_users:
            logging.warning(f'{selected} was in excluded history: {excluded_users}, re-selecting...')
            return self.select(users)
        else:
            logging.info(f'users: {users}, selected user is: {selected}')
            self.history = (self.history + [selected])[-2:]
            return selected


def get_congrats_msg():
    return random.choice([
        "صاحب الحظ السعيد اليوم هو",
        "يا هناك يا سعدك يا",
        "اليوم يومك النهارده يا",
        "مبروك عليك ... هتطلب لنا اليوم يا"
    ])
