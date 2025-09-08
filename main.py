import logging
from datetime import datetime, time as dtime

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import config
import database
import scheduler

logging.basicConfig(level=logging.INFO)
database.init_db()

def is_admin(user_id):
    return user_id in config.ADMIN_IDS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("SmartOfis Botga xush kelibsiz.")

async def add_employee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Faqat admin uchun.")
    args = context.args
    if len(args) < 4:
        return await update.message.reply_text("Foydalanish: /add_employee ism telegram_id boshlanish_vaqti tugash_vaqti")
    name, tg_id, work_start, work_end = args[0], int(args[1]), args[2], args[3]
    database.add_employee(name, tg_id, work_start, work_end)
    await update.message.reply_text(f"{name} qo‘shildi.")

async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    if not (dtime(0, 0) <= now.time() <= dtime(8, 30)):
        return await update.message.reply_text("Planni ertalab 00:00–08:30 oralig‘ida yuboring.")
    emp = database.get_employee_by_telegram_id(update.effective_user.id)
    if not emp:
        return await update.message.reply_text("Siz tizimda xodim sifatida ro‘yxatdan o‘tmagansiz.")
    plan_text = " ".join(context.args)
    database.submit_plan(emp['id'], now.strftime("%Y-%m-%d"), plan_text, now.strftime("%H:%M"))
    await update.message.reply_text("Planni qabul qildik.")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    if not (dtime(18, 0) <= now.time() <= dtime(21, 0)):
        return await update.message.reply_text("Reportni 18:00–21:00 oralig‘ida yuboring.")
    emp = database.get_employee_by_telegram_id(update.effective_user.id)
    if not emp:
        return await update.message.reply_text("Siz tizimda xodim sifatida ro‘yxatdan o‘tmagansiz.")
    report_text = " ".join(context.args)
    database.submit_report(emp['id'], now.strftime("%Y-%m-%d"), report_text, now.strftime("%H:%M"))
    await update.message.reply_text("Report qabul qilindi.")

async def jarimalarim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emp = database.get_employee_by_telegram_id(update.effective_user.id)
    if not emp:
        return await update.message.reply_text("Siz tizimda xodim sifatida ro‘yxatdan o‘tmagansiz.")
    month = datetime.now().strftime("%Y-%m")
    fines = database.get_fines_by_employee(emp['id'], month)
    if not fines:
        return await update.message.reply_text("Sizda bu oyda jarima yo‘q.")
    text = "Oyning jarimalari:\n"
    for f in fines:
        text += f"{f['date']} - {f['type']}: {f['amount']} so'm ({f['reason']})\n"
    await update.message.reply_text(text)

async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    emp = database.get_employee_by_telegram_id(update.effective_user.id)
    if not emp:
        return await update.message.reply_text("Siz tizimda xodim sifatida ro‘yxatdan o‘tmagansiz.")
    database.log_checkin(emp['id'], now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), 'bot')
    await update.message.reply_text("Ishga kelish belgilandi.")

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    emp = database.get_employee_by_telegram_id(update.effective_user.id)
    if not emp:
        return await update.message.reply_text("Siz tizimda xodim sifatida ro‘yxatdan o‘tmagansiz.")
    database.log_checkout(emp['id'], now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), 'bot')
    await update.message.reply_text("Ishdan ketish belgilandi.")

def main():
    scheduler.start_scheduler()
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_employee", add_employee))
    app.add_handler(CommandHandler("plan", plan))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("jarimalarim", jarimalarim))
    app.add_handler(CommandHandler("checkin", checkin))
    app.add_handler(CommandHandler("checkout", checkout))
    app.run_polling()

if __name__ == "__main__":
    main()
