#!/usr/bin/env python
# pylint: disable=unused-argument
import logging
import os
import random
import threading

from telebot import BotApp
from telegram import Update
from telegram.ext import ContextTypes

import food

bot = BotApp()
users = []
order = {}


@bot.command(text=True)
async def capture_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    threading.Thread(target=_capture_order, args=(update,)).start()


def _capture_order(update: Update):
    global users, order

    message = update.edited_message if update.edited_message else update.message
    captured_user = f'{update.effective_user.first_name} {update.effective_user.last_name or ""}'

    if food.is_food(message.text):
        order[(message.id, captured_user)] = message.text
        logging.info(f'adding {message.text} to the order {order}')
        if captured_user not in users: users.append(captured_user)
        # message.reply_text('تمت الإضافة')
    else:
        logging.warning(f'{message.text} is not food, skipping...')


@bot.command(name="ping", desc="اختبار البوت")
async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Pong!")


@bot.command(name="yalla", desc="اختيار اسم عشوائي من القائمة")
async def yalla_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await select_user(context, update.message.chat_id)


@bot.command(name="add", desc="إضافة اسم إلى القائمة")
async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global users
    user = " ".join(context.args)
    if user:
        users.append(user)
        await update.message.reply_text(f"تم إضافة {user} إلى القائمة ")
    else:
        await update.message.reply_text("خطأ، يجب كتابة الإسم")


@bot.command(name="list", desc="عرض جميع الأسماء في القائمة")
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global users
    await update.message.reply_text(
        "قائمة الأسماء هي: \n" + "\n".join(users) if len(users) > 0 else "قائمة المستخدمين فارغة")


@bot.command(name="clear", desc="مسح جميع الأسماء من القائمة")
async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global users, order
    users = []
    order = {}
    await update.message.reply_text("تم مسح جميع الأسماء من القائمة")


@bot.command(name="summarize", desc="تلخيص الطلب")
async def summarize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global users, order
    if len(order) == 0:
        await update.message.reply_text("لا يوجد طلبات")
        return

    food_list = "\n".join(f'{u} -> {o}' for (_, u), o in order.items())
    logging.info(food_list)
    await update.message.reply_text(food_list)


@bot.command(name="about", desc="عن البوت")
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'لانشي بوت مساعدك في طلب الغداء\n\n'
        'تقوم فكرة عمل البوت بأنه يقوم بفحص الرسائل و إذا كانت الرسالة تحتوي على اسم طعام، '
        'يقوم البوت بإضافة اسم المرسل لقائمة المستخدمين المحتمل أن يتم اختياره لطلب الغداء'
    )


@bot.job(time=os.getenv("HEADS_UP_TIME", "08:00"))
async def send_lunch_headsup(context: ContextTypes.DEFAULT_TYPE, chat_id):
    global users, order
    users = []
    order = {}
    await context.bot.send_message(chat_id, text="يلا يا شباب أبدأو ضيفو طلابتكم")


@bot.job(time=os.getenv("SELECTION_TIME", "09:30"), enabled=False)
async def send_lunch_selection(context: ContextTypes.DEFAULT_TYPE, chat_id):
    await select_user(context, chat_id)


async def select_user(context: ContextTypes.DEFAULT_TYPE, chat_id):
    global users
    if len(users) > 0:
        selected_user = random.choice(users)
        logging.info(f'we have this list of users: {users}, randomly selected user is: {selected_user}')
        await context.bot.send_message(chat_id=chat_id, text="صاحب الحظ السعيد اليوم هو" + f" {selected_user} 🎉")
    else:
        logging.warning(f'user list might be empty: {users}')
        await context.bot.send_message(chat_id=chat_id, text="قائمة المستخدمين فارغة")


if __name__ == '__main__':
    bot.help(desc="عرض المساعدة")
    bot.application.run_polling(allowed_updates=Update.ALL_TYPES)
