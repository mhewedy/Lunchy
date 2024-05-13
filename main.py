#!/usr/bin/env python
# pylint: disable=unused-argument
import logging
import os
import random

import dateutil.parser
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

chat_id = os.getenv("CHAT_ID", -4201961515)
users = []


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Pong!")


async def capture_names(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global users, chat_id
    chat_id = update.message.chat_id

    elected_user = update.effective_user.first_name + " " + update.effective_user.last_name
    if elected_user not in users: users.append(elected_user)
    logger.info(f'user {elected_user} added!, {users}')


async def send_lunch_headsup(context):
    global users
    users = []  # clean
    await context.bot.send_message(chat_id=chat_id, text="""
    يلا يا شباب أبدأو ضيفو طلابتكم ...
     خدو بالكم اللي هيبعت حاجه في الشات من دلوقتي لحد ما يتم اختيار الإسم هيكون من ضمن الناس اللي هتدخل في الاختيار
    """)


async def send_lunch_election(context):
    global users

    if len(users) > 0:
        selected_user = random.choice(users)
        logger.info(f'selected user is: {selected_user}')
        await context.bot.send_message(chat_id=chat_id, text=f' سعيد الحظ النهارده هو{selected_user}!')
    else:
        logger.warning('user list is empty')


def main() -> None:
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_names))

    application.add_handler(CommandHandler("ping", ping_command))

    headsup_time = dateutil.parser.parse(os.getenv("HEADS_UP_TIME", "08:45")).time()
    logger.info(f'heads up time is set to: {headsup_time} UTC')
    application.job_queue.run_daily(send_lunch_headsup, time=headsup_time)

    election_time = dateutil.parser.parse(os.getenv("ELECTION_TIME", "10:00")).time()
    logger.info(f'heads up time is set to: {election_time} UTC')
    application.job_queue.run_daily(send_lunch_election, time=election_time)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
