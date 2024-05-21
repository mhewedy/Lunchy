import json
import logging
import os
import random
from abc import abstractmethod, ABC


class HistoryManager(ABC):
    def __init__(self):
        self.history = []

    @abstractmethod
    def load_history(self):
        pass

    def save_history(self, h):
        self.history = h


class InMemoryHistoryManager(HistoryManager):
    def load_history(self):
        pass


class FileSystemHistoryManager(HistoryManager):
    def __init__(self, file_path='~/.lunchy/history.json'):
        super().__init__()
        self.file_path = os.path.expanduser(file_path)
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
            self.save_history(self.history)

    def save_history(self, h):
        super().save_history(h)
        with open(self.file_path, 'w') as file:
            json.dump(self.history, file)


class UserSelector:
    def __init__(self, exclude_gap=0, history_manager=FileSystemHistoryManager()):
        self.exclude_gap = exclude_gap
        self.history_manager = history_manager

    def select(self, users):
        if not users:
            raise ValueError('users list should not be empty')

        uniq_len = len(list(set(users)))
        excluded_users = self.history_manager.history[
                         len(self.history_manager.history) -
                         (uniq_len - 1 if uniq_len <= self.exclude_gap else self.exclude_gap):
                         ]
        selected = random.choice(users)

        if selected in excluded_users:
            logging.warning(f'{selected} was in excluded history: {excluded_users}, re-selecting...')
            return self.select(users)
        else:
            logging.info(f'users: {users}, selected user is: {selected}')
            self.history_manager.save_history((self.history_manager.history + [selected])[-10:])
            return selected

    def clear_history(self):
        self.history_manager.save_history([])
