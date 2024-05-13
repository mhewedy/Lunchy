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

selected_user_msg = "صاحب الحظ السعيد اليوم هو"

chat_id = os.getenv("CHAT_ID", -4201961515)
users = []


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("ping command received")
    await update.message.reply_text("Pong!")


async def yalla_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("yalla command received")
    selected_user = select_user()
    if selected_user:
        await update.message.reply_text(selected_user_msg + f" {selected_user}")


async def capture_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global users, chat_id
    chat_id = update.message.chat_id

    captured_user = update.effective_user.first_name + " " + update.effective_user.last_name
    if captured_user not in users:
        users.append(captured_user)
        logger.info(f'user {captured_user} added!, {users}')


async def send_lunch_headsup(context):
    logger.info("send_lunch_headsup")
    global users
    users = []  # clean
    await context.bot.send_message(chat_id=chat_id, text="يلا يا شباب أبدأو ضيفو طلابتكم ...")


async def send_lunch_election(context):
    logger.info("send_lunch_election")
    selected_user = select_user()
    if selected_user:
        await context.bot.send_message(chat_id=chat_id, text=selected_user_msg + f" {selected_user}")


async def select_user():
    global users

    if len(users) > 0:
        selected_user = random.choice(users)
        logger.info(f'selected user is: {selected_user}')
        users = []
        logger.info(f'resetting user list!')
        return selected_user
    else:
        logger.warning('user list is empty')
        return None


def main() -> None:
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_users))

    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CommandHandler("yalla", yalla_command))

    headsup_time = dateutil.parser.parse(os.getenv("HEADS_UP_TIME", "08:30")).time()
    logger.info(f'heads up time is set to: {headsup_time} UTC')
    application.job_queue.run_daily(send_lunch_headsup, time=headsup_time)

    election_time = dateutil.parser.parse(os.getenv("ELECTION_TIME", "10:00")).time()
    logger.info(f'heads up time is set to: {election_time} UTC')
    application.job_queue.run_daily(send_lunch_election, time=election_time)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
