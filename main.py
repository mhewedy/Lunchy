#!/usr/bin/env python
# pylint: disable=unused-argument
import logging
import os
import random

import dateutil.parser
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger(__name__)

chat_id = os.getenv("CHAT_ID", -4201961515)
users = []


async def capture_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global users, chat_id
    chat_id = update.message.chat_id
    captured_user = update.effective_user.first_name + " " + update.effective_user.last_name
    if captured_user not in users:
        users.append(captured_user)
        log.info(f'user {captured_user} added!, {users}')


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.info("ping command received")
    await update.message.reply_text("Pong!")


async def yalla_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.info("yalla command received")
    await select_user(context)


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global users
    user = " ".join(context.args)
    log.info(f"add_command: {user}")
    if user:
        users.append(user)
        await update.message.reply_text(f"تم إضافة {user} إلى القائمة ")
    else:
        await update.message.reply_text("خطأ، يجب كتابة الإسم")


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global users
    log.info(f"list_command: {users}")
    await update.message.reply_text(
        "قائمة الأسماء هي: \n" + "\n".join(users) if len(users) > 0 else "قائمة المستخدمين فارغة")


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global users
    log.info("clear_command")
    users = []
    await update.message.reply_text("تم مسح جميع الأسماء من القائمة")


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global users
    log.info(f"list_command: {users}")
    await update.message.reply_text("""
يقوم البوت بحفظ اسماء المشاركين في المحادثه قبيل معاد الغداء
و عند وقت طلب الغداء يقوم البوت بإختيار اسم عشوائي من القائمة
يمكنك التحكم في القائمة بإستخدام اوامر القائمة كعرض القائمه و مسحها و الإضافة فيها
يمكن أيضا تعجيل اختيار الاسم في أي وقت
    """)


def help_clojure(cmds_fn):
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        global users
        log.info(f"list_command: {users}")
        await update.message.reply_text("\n".join(f'/{c} -> {msg}' for (c, _, msg) in cmds_fn()))

    return help_command


async def send_lunch_headsup(context: ContextTypes.DEFAULT_TYPE):
    global users
    log.info("send_lunch_headsup")
    users = []
    await context.bot.send_message(chat_id=chat_id, text="يلا يا شباب أبدأو ضيفو طلابتكم")


async def send_lunch_election(context: ContextTypes.DEFAULT_TYPE):
    log.info("send_lunch_election")
    await select_user(context)


async def select_user(context: ContextTypes.DEFAULT_TYPE):
    global users
    if len(users) > 0:
        selected_user = random.choice(users)
        log.info(f'we have this list of users: {users}, randomly selected user is: {selected_user}')
        await context.bot.send_message(chat_id=chat_id, text="صاحب الحظ السعيد اليوم هو" + f" {selected_user}")
    else:
        log.warning(f'user list might be empty: {users}')
        await context.bot.send_message(chat_id=chat_id, text="قائمة المستخدمين فارغة")


def main() -> None:
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_users))

    cmds = []

    cmds = [
        ("ping", ping_command, "اختبار البوت"),
        ("yalla", yalla_command, "اختيار اسم عشوائي من القائمة"),
        ("add", add_command, "إضافة اسم إلى القائمة"),
        ("list", list_command, "عرض جميع الأسماء في القائمة"),
        ("clear", clear_command, "مسح جميع الأسماء من القائمة"),
        ("about", about_command, "عن البوت"),
        ("help", help_clojure(lambda: cmds), "عرض المساعدة")
    ]
    for (cmd, func, _) in cmds:
        application.add_handler(CommandHandler(cmd, func))

    jobs = [
        ("heads up", os.getenv("HEADS_UP_TIME", "08:30"), send_lunch_headsup),
        ("election", os.getenv("ELECTION_TIME", "10:00"), send_lunch_election)
    ]
    for (name, t, func) in jobs:
        parsed_time = dateutil.parser.parse(t).time()
        log.info(f'{name} time is set to: {parsed_time} UTC')
        application.job_queue.run_daily(func, time=parsed_time)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
