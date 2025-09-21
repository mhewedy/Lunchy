import json
import logging
import os
import random
from abc import abstractmethod, ABC

import util


class HistoryManager(ABC):
    def __init__(self):
        # history: {chat_id: [user1, user2, ...]}
        self.history = {}

    @abstractmethod
    def load_history(self):
        pass

    def save_history(self, chat_id, h):
        self.history[chat_id] = h


class InMemoryHistoryManager(HistoryManager):
    def load_history(self):
        pass


class FileSystemHistoryManager(HistoryManager):
    def __init__(self, file_path=util.get_root_fs() + '/selection_history.json'):
        super().__init__()
        self.file_path = os.path.expanduser(file_path)
        self.load_history()

    def load_history(self):
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                loaded_history = json.load(file)
                self.history = {int(chat_id): hist for chat_id, hist in loaded_history.items()}
        else:
            self.history = {}
            self.save_history_all()

    def save_history(self, chat_id, h):
        super().save_history(chat_id, h)
        self.save_history_all()

    def save_history_all(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.history, file)


class UserSelector:
    def __init__(self, exclude_gap=0, history_manager=None):
        self.exclude_gap = exclude_gap
        self.history_manager = history_manager or FileSystemHistoryManager()

    def select(self, chat_id, users):
        if not users:
            raise ValueError('users list should not be empty')

        chat_history = self.history_manager.history.get(chat_id, [])

        uniq_len = len(list(set(users)))
        excluded_users = chat_history[
            len(chat_history) -
            (uniq_len - 1 if uniq_len <= self.exclude_gap else self.exclude_gap):
        ]
        selected = random.choice(users)

        if selected in excluded_users:
            logging.warning(f'{selected} was in excluded history: {excluded_users}, re-selecting...')
            return self.select(chat_id, users)
        else:
            # Save only last 10 selections
            logging.info(f'users: {users}, selected user is: {selected}')
            self.history_manager.save_history(chat_id, (chat_history + [selected])[-10:])
            return selected

    def clear_history(self, chat_id):
        self.history_manager.save_history(chat_id, [])
