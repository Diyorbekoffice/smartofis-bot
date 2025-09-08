from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from telegram import Bot
from config import GROUP_CHAT_ID, BOT_TOKEN

def send_plan_reminder():
    bot = Bot(BOT_TOKEN)
    bot.send_message(chat_id=GROUP_CHAT_ID, text="⏰ Plan yozish vaqti boshlandi!")

def send_report_reminder():
    bot = Bot(BOT_TOKEN)
    bot.send_message(chat_id=GROUP_CHAT_ID, text="📋 Report yozish vaqti boshlandi!")

def send_daily_fines():
    from database import get_daily_summary
    today = datetime.now().strftime("%Y-%m-%d")
    summary = get_daily_summary(today)
    if summary:
        text = "📊 Bugungi jarimalar:\n"
        for row in summary:
            text += f"{row['name']}: {row['type']} — {row['amount']} so'm ({row['reason']})\n"
    else:
        text = "📊 Bugun jarima yo‘q!"
    bot = Bot(BOT_TOKEN)
    bot.send_message(chat_id=GROUP_CHAT_ID, text=text)

def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Tashkent")
    scheduler.add_job(send_plan_reminder, trigger='cron', hour=8, minute=50)
    scheduler.add_job(send_report_reminder, trigger='cron', hour=21, minute=0)
    scheduler.add_job(send_daily_fines, trigger='cron', hour=21, minute=30)
    scheduler.start()
