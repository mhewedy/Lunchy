import time
from typing import Callable, Any

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
