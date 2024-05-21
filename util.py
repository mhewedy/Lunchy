import json
import logging
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


class HistoryManager:
    def __init__(self):
        self.history = []

    def load_history(self):
        pass

    def save_history(self):
        pass


class InMemoryHistoryManager(HistoryManager):
    def __init__(self):
        super().__init__()


class FileSystemHistoryManager(HistoryManager):
    def __init__(self, file_path=None):
        super().__init__()
        if file_path is None:
            file_path = os.path.expanduser('~/.lunchy/history.json')
        self.file_path = file_path
        self.load_history()

    def load_history(self):
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                self.history = json.load(file)
        else:
            self.history = []
            self.save_history()

    def save_history(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.history, file)


class UserSelector:
    def __init__(self, history_manager=InMemoryHistoryManager()):
        self.selection_gap = 2
        self.history_manager = history_manager

    def select(self, users):
        if not users:
            raise ValueError('users list should not be empty')

        uniq_len = len(list(set(users)))
        excluded_users = self.history_manager.history[
                         len(self.history_manager.history) -
                         (uniq_len - 1 if uniq_len <= self.selection_gap else self.selection_gap):
                         ]
        selected = random.choice(users)

        if selected in excluded_users:
            logging.warning(f'{selected} was in excluded history: {excluded_users}, re-selecting...')
            return self.select(users)
        else:
            logging.info(f'users: {users}, selected user is: {selected}')
            self.history_manager.history = (self.history_manager.history + [selected])[-2:]
            self.history_manager.save_history()
            return selected

    def clear_history(self):
        self.history_manager.history = []


def get_congrats_msg():
    return random.choice([
        "صاحب الحظ السعيد اليوم هو",
        "يا هناك يا سعدك يا",
        "اليوم يومك النهارده يا",
        "مبروك عليك ... هتطلب لنا اليوم يا"
    ])
