#!/usr/bin/env python
# pylint: disable=unused-argument
import asyncio
import logging
import os
import random

from telebot import BotApp
from telegram import Update
from telegram.ext import ContextTypes

import food

bot = BotApp()
orders = {}


@bot.command(text=True)
async def capture_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async def capture():
        (message, is_edit) = (update.message, False) if update.message else (update.edited_message, True)

        if food.is_food(message.text):
            user = f'{update.effective_user.first_name} {update.effective_user.last_name or ""}'
            orders[(message.id, user)] = message.text
            logging.info(f'adding {message.text} to the order {orders}')

            await message.reply_text('تم التعديل' if is_edit else 'تمت الإضافة')
        else:
            logging.warning(f'{message.text} is not food, skipping...')

    # no await
    asyncio.create_task(capture())  # noinspection PyTypeChecker


@bot.command(name="add", desc="*إضافة طلب إلى القائمة")
async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order = " ".join(context.args)
    if not order:
        await update.message.reply_text("خطأ، قم بكتابة الطلب")
        return

    user = f'{update.effective_user.first_name} {update.effective_user.last_name or ""}'
    orders[(update.message.id, user)] = order
    await update.message.reply_text('تمت الإضافة')


@bot.command(name="summarize", desc="تلخيص الطلبات")
@bot.command(name="list", desc="عرض الطلبات")
async def summarize_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(orders) == 0:
        await update.message.reply_text("لا توجد طلبات")
        return

    food_list = "\n".join(f'{u} -> {o}' for (_, u), o in orders.items())
    logging.info(food_list)
    await update.message.reply_text(food_list)


@bot.command(name="yalla", desc="اختيار اسم عشوائي من القائمة")
async def yalla_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await select_user(context, update.message.chat_id)


@bot.command(name="clear", desc="المسح و البدأ من جديد")
async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global orders
    orders = {}
    await update.message.reply_text("تم المسح بنجاح")


@bot.command(name="ping", desc="اختبار البوت")
async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Pong!")


@bot.command(name="about", desc="عن البوت")
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '"لانشي بوت" مساعدك في طلب الغداء\n\n'
        'تقوم فكرة عمل البوت بأنه يقوم بفحص الرسائل و إذا كانت الرسالة تحتوي على اسم طعام، '
        'يقوم البوت بإضافة الطلب بشكل آلي إلى قائمة الطلبات\n\n'
        'إذا لم يقم البوت بإضافة الطلب بشكل آلي (ربما لعدم تعرفه على نوع الطعام)، يمكن إضافته عن طريق الأمر "/add" \n\n'
        'في النهاية يمكنك عرض الطلبات الحالية عن طريق الأمر "/summarize" أو "/list" '
        'و بعد مراجعة الطلب يتم اختيار احد الأشخاص بشكل عشوائي عن طريق الأمر "/yalla"'
    )


@bot.job(time=os.getenv("HEADS_UP_TIME", "08:00"))
async def send_lunch_headsup(context: ContextTypes.DEFAULT_TYPE, chat_id):
    global orders
    orders = {}
    await context.bot.send_message(chat_id, text="يلا يا شباب أبدأو ضيفو طلابتكم")


@bot.job(time=os.getenv("SELECTION_TIME", "09:30"), enabled=False)
async def send_lunch_selection(context: ContextTypes.DEFAULT_TYPE, chat_id):
    await select_user(context, chat_id)


async def select_user(context: ContextTypes.DEFAULT_TYPE, chat_id):
    users = [user for (_, user), _ in orders.items()]
    if len(users) > 0:
        selected = random.choice(users)
        logging.info(f'we have this list of users: {users}, randomly selected user is: {selected}')
        await context.bot.send_message(chat_id=chat_id, text="صاحب الحظ السعيد اليوم هو" + f" {selected} 🎉")
    else:
        logging.warning(f'user list might be empty: {users}')
        await context.bot.send_message(chat_id=chat_id, text="قائمة الطلبات فارغة")


if __name__ == '__main__':
    bot.help(desc="عرض المساعدة")
    bot.application.run_polling(allowed_updates=Update.ALL_TYPES)
