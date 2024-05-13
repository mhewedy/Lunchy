#!/usr/bin/env python
# pylint: disable=unused-argument
import logging
import os
import random

import dateutil.parser
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler

SELECTED_USER_MSG = "صاحب الحظ السعيد اليوم هو"

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger(__name__)

chat_id = os.getenv("CHAT_ID", -4201961515)
users = []


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.info("ping command received")
    await update.message.reply_text("Pong!")


async def yalla_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.info("yalla command received")
    await select_user(context)


async def capture_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global users, chat_id
    chat_id = update.message.chat_id
    captured_user = update.effective_user.first_name + " " + update.effective_user.last_name
    if captured_user not in users:
        users.append(captured_user)
        log.info(f'user {captured_user} added!, {users}')


async def send_lunch_headsup(context: ContextTypes.DEFAULT_TYPE):
    global users
    log.info("send_lunch_headsup")
    users = []  # clean
    await context.bot.send_message(chat_id=chat_id, text="يلا يا شباب أبدأو ضيفو طلابتكم ...")


async def send_lunch_election(context: ContextTypes.DEFAULT_TYPE):
    log.info("send_lunch_election")
    await select_user(context)


async def select_user(context: ContextTypes.DEFAULT_TYPE):
    global users
    if len(users) > 0:
        selected_user = random.choice(users)
        log.info(f'we have this list of users: {users}, randomly selected user is: {selected_user}')
        await context.bot.send_message(chat_id=chat_id, text=SELECTED_USER_MSG + f" {selected_user}")
    else:
        log.warning(f'user list might be empty: {users}')


def main() -> None:
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_users))
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CommandHandler("yalla", yalla_command))

    headsup_time = dateutil.parser.parse(os.getenv("HEADS_UP_TIME", "08:30")).time()
    log.info(f'heads up time is set to: {headsup_time} UTC')
    application.job_queue.run_daily(send_lunch_headsup, time=headsup_time)

    election_time = dateutil.parser.parse(os.getenv("ELECTION_TIME", "10:00")).time()
    log.info(f'heads up time is set to: {election_time} UTC')
    application.job_queue.run_daily(send_lunch_election, time=election_time)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
