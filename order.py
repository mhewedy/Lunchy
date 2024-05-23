import ast
import json
import logging
from abc import ABC
from pathlib import Path

import cache
import util


class OrderManager(ABC):
    def __init__(self):
        self.orders = {}

    def add_order(self, message_id, user, order):
        cache.put('food', order, True)
        self.orders[(message_id, user)] = order

    def delete_order(self, user):
        deleted_orders = [(key, self.orders[key]) for key in list(self.orders) if key[1] == user]
        for key, _ in deleted_orders:
            del self.orders[key]
        return deleted_orders

    def list_orders(self):
        return self.orders

    def clear_orders(self):
        self.orders = {}


class InMemoryOrderManager(OrderManager):
    pass


class FileSystemOrderManager(OrderManager):
    def __init__(self, file_path=util.get_root_fs() + '/orders.json'):
        super().__init__()
        self.file_path = Path(file_path)
        logging.info('loading orders from: {}'.format(self.file_path))
        if self.file_path.exists():
            with open(self.file_path, 'r') as file:
                self.orders = {ast.literal_eval(k): v for k, v in json.load(file).items()}
                logging.info('loaded orders {}'.format(self.orders))
        else:
            logging.error('orders file does not exist, creating one...')
            self._save_to_file()

    def add_order(self, message_id, user, order):
        super().add_order(message_id, user, order)
        self._save_to_file()

    def delete_order(self, user):
        deleted_orders = super().delete_order(user)
        self._save_to_file()
        return deleted_orders

    def clear_orders(self):
        super().clear_orders()
        self._save_to_file()

    def _save_to_file(self):
        with open(self.file_path, 'w') as file:
            json.dump({str(k): v for k, v in self.orders.items()}, file)
