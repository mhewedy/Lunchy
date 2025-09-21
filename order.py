import ast
import json
import logging
from abc import ABC
from pathlib import Path

import cache
import util


class OrderManager(ABC):
    def __init__(self):
        # orders: {chat_id: {(message_id, user): order}}
        self.orders = {}

    def add_order(self, chat_id, message_id, user, order):
        if chat_id not in self.orders:
            self.orders[chat_id] = {}
        cache.put('food', order, True)
        self.orders[chat_id][(message_id, user)] = order

    def delete_order(self, chat_id, user):
        if chat_id not in self.orders:
            return []
        deleted_orders = [(key, self.orders[chat_id][key]) for key in list(self.orders[chat_id]) if key[1] == user]
        for key, _ in deleted_orders:
            del self.orders[chat_id][key]
        return deleted_orders

    def list_orders(self, chat_id):
        return self.orders.get(chat_id, {})

    def clear_orders(self, chat_id):
        self.orders[chat_id] = {}


class InMemoryOrderManager(OrderManager):
    pass


class FileSystemOrderManager(OrderManager):
    def __init__(self, file_path=util.get_root_fs() + '/orders.json'):
        super().__init__()
        self.file_path = Path(file_path)
        logging.info('loading orders from: {}'.format(self.file_path))
        if self.file_path.exists():
            with open(self.file_path, 'r') as file:
                # orders structure: {chat_id: {str((message_id, user)): order}}
                loaded_orders = json.load(file)
                self.orders = {
                    int(chat_id): {ast.literal_eval(k): v for k, v in chat_orders.items()}
                    for chat_id, chat_orders in loaded_orders.items()
                }
                logging.info('loaded orders {}'.format(self.orders))
        else:
            logging.error('orders file does not exist, creating one...')
            self._save_to_file()

    def add_order(self, chat_id, message_id, user, order):
        super().add_order(chat_id, message_id, user, order)
        self._save_to_file()

    def delete_order(self, chat_id, user):
        deleted_orders = super().delete_order(chat_id, user)
        self._save_to_file()
        return deleted_orders

    def clear_orders(self, chat_id):
        super().clear_orders(chat_id)
        self._save_to_file()

    def _save_to_file(self):
        with open(self.file_path, 'w') as file:
            json.dump({chat_id: {str(k): v for k, v in chat_orders.items()} for chat_id, chat_orders in self.orders.items()}, file)
