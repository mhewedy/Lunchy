import logging
import random
import time
from typing import Callable
from typing import List, Any

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


def current_user(update: Update):
    return update.effective_user.full_name


async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    administrators = await context.bot.get_chat_administrators(update.message.chat_id)

    for admin in administrators:
        if admin.user.id == update.effective_user.id:
            return True

    return False


class UserSelector:
    def __init__(self):
        self.history = []

    def select(self, users: List[str]) -> [str | None]:
        distinct = list(set(users))
        excluded_users = [] if len(distinct) == 1 else self.history[-1:] if len(distinct) == 2 else self.history[-2:]

        selected = random.choice(users)

        if selected in excluded_users:
            logging.warning(f'{selected} was in excluded history: {excluded_users}, re-selecting...')
            return self.select(users)
        else:
            self.history.append(selected)
            # always keep the last 2 elements in the history, for comparison
            self.history = self.history[-2:]
            return selected


def get_congrats_msg():
    return random.choice([
        "صاحب الحظ السعيد اليوم هو",
        "يا هناك يا سعدك يا",
        "اليوم يومك النهارده يا",
        "مبروك عليك ... هتطلب لنا اليوم يا"
    ])
