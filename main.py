#!/usr/bin/env python
# pylint: disable=unused-argument
import asyncio
import logging
import os
from datetime import datetime

from telebot import BotApp
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import food
import util
from order_manager import FileSystemOrderManager
from selection import UserSelector

bot = BotApp()
userSelector = UserSelector()
order_manager = FileSystemOrderManager()


@bot.command(text=True)
async def capture_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async def capture():
        (message, is_edit) = (update.message, False) if update.message else (update.edited_message, True)

        if food.is_food(message.text):
            user = util.current_user(update)
            order_manager.add_order(message.id, user, message.text)
            logging.info(f'adding {message.text} to the order {order_manager.list_orders()}')

            await message.reply_text('تم التعديل' if is_edit else 'تمت الإضافة')
        else:
            logging.warning(f'{message.text} is not food, skipping...')

    # no await
    asyncio.create_task(capture())  # noinspection PyTypeChecker


@bot.command(name="add", desc="*إضافة طلبك")
async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order = " ".join(context.args)
    if not order:
        await update.message.reply_text("خطأ، قم بكتابة الطلب")
        return

    user = util.current_user(update)
    order_manager.add_order(update.message.id, user, order)
    await update.message.reply_text('تمت الإضافة')


@bot.command(name="delete", desc="مسح طلبك")
async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = util.current_user(update)
    deleted_orders = order_manager.delete_order(user)
    if deleted_orders:
        for (_, _), o in deleted_orders:
            await update.message.reply_text(f'تم مسح طلبك "{o}" بنجاح')
    else:
        await update.message.reply_text('لا توجد طلبات')


@bot.command(name="list", desc="عرض الطلبات")
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orders = order_manager.list_orders()
    if not orders:
        await update.message.reply_text("لا توجد طلبات")
        return

    food_list = "\n".join(f'{u} -> {o}' for (_, (_, u)), o in orders.items())
    logging.info(food_list)
    await update.message.reply_text(food_list)


@bot.command(name="yalla", desc="اختيار اسم عشوائي")
async def yalla_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await select_user(context, update.message.chat_id)


@bot.command(name="clear", desc="مسح جميع الطلبات", hidden=True)
async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await util.is_admin(update, context):
        await update.message.reply_text("هذه الخاصية متاحة فقط للأدمن")
        return

    order_manager.clear_orders()
    msg = "تم مسح جميع الطلبات بنجاح"
    if "+selection_history" in context.args:
        msg += " و تم مسح جميع اختيارات المستخدمين أيضا"
        userSelector.clear_history()
    await update.message.reply_text(msg)


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
        'في النهاية يمكنك عرض الطلبات الحالية عن طريق الأمر "/list" '
        'و بعد مراجعة الطلب يتم اختيار احد الأشخاص بشكل عشوائي عن طريق الأمر "/yalla"'
    )


@bot.job(time=os.getenv("HEADS_UP_TIME", "08:00"))
async def send_lunch_headsup(context: ContextTypes.DEFAULT_TYPE, chat_id):
    if datetime.today().weekday() in [4, 5]:
        logging.info('today is weekend, job will be suspended')
        return

    order_manager.clear_orders()
    await context.bot.send_message(chat_id, text="يلا يا شباب أبدأو ضيفو طلابتكم")


@bot.job(time=os.getenv("SELECTION_TIME", "09:30"), enabled=False)
async def send_lunch_selection(context: ContextTypes.DEFAULT_TYPE, chat_id):
    await select_user(context, chat_id)


async def select_user(context: ContextTypes.DEFAULT_TYPE, chat_id):
    users = [user for (_, user), _ in order_manager.list_orders().items()]
    if users:
        uid, u = userSelector.select(users)
        mention_text = f"<a href='tg://user?id={uid}'>{u}</a>"
        await context.bot.send_message(chat_id=chat_id, text=util.get_congrats_msg() + f" {mention_text}🎉",
                                       parse_mode=ParseMode.HTML)
    else:
        logging.warning(f'user list might be empty: {users}')
        await context.bot.send_message(chat_id=chat_id, text="قائمة الطلبات فارغة")


if __name__ == '__main__':
    bot.help(desc="عرض المساعدة")
    bot.application.run_polling(allowed_updates=Update.ALL_TYPES)
