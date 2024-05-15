import logging
import os

import dateutil.parser
from telegram import Update
from telegram.ext import Application
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging = logging.getLogger(__name__)

chat_id = os.getenv("CHAT_ID", -4201961515)
logging.info(f'CHAT_ID: {chat_id}')


class BotApp:

    def __init__(self):
        self.application = Application.builder().token(os.getenv("BOT_TOKEN")).build()
        self.cmds = []

    def command(self, name=None, desc=None, text=False):
        def wrapper(func):
            if name: self.cmds.append((name, desc))

            def wrapped_func(*args, **kwargs):
                global chat_id
                logging.info(f"invoking command: {func.__name__}")

                (update, _) = args
                chat_id = update.edited_message.chat_id if update.edited_message else update.message.chat_id
                logging.info(f'setting g_chat_id to: {chat_id}')

                return func(*args, **kwargs)

            if name: logging.info(f"declaring command: {name}")
            if text:
                self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, wrapped_func))
            else:
                self.application.add_handler(CommandHandler(name, wrapped_func))
            return wrapped_func

        return wrapper

    def job(self, time, enabled=True):
        def wrapper(func):
            if enabled:
                logging.info(f'scheduling {func.__name__} at: {dateutil.parser.parse(time).time()} UTC')

            def wrapped_func(*args, **kwargs):
                logging.info(f"invoking job: {func.__name__}")
                new_args = args + (chat_id,)
                result = func(*new_args, **kwargs)
                return result

            if enabled:
                wrapped_func.__name__ = f'w/{func.__name__}'
                self.application.job_queue.run_daily(wrapped_func, time=dateutil.parser.parse(time).time())
            return wrapped_func

        return wrapper

    def help(self):
        self.cmds.append(("help", "عرض المساعدة"))
        self.application.add_handler(CommandHandler("help", self._help_command))
        self.application.add_handler(MessageHandler(filters.COMMAND, self._help_command))

    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("\n".join(f'/{name} -> {desc}' for (name, desc) in self.cmds))
